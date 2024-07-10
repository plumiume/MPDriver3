# Copyright 2024 The MPDriver3 Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import traceback
from typing import TypedDict, NamedTuple, TextIO
from typing import Sized, Iterable, Iterator, Container, Sequence, Mapping
from typing import TypeVar, Generic, Unpack, Any, overload, TYPE_CHECKING
from types import TracebackType
from collections import deque
import heapq
import time
from datetime import datetime
from tqdm import tqdm

from threading import Thread
from multiprocessing import Process, Queue, Lock as _Lock, parent_process
from multiprocessing.synchronize import Lock
from multiprocessing.managers import SyncManager

_T = TypeVar("_T")

class TqdmKwargs(TypedDict):
    desc: str | None
    total: float | None
    leave: bool
    file: TextIO | None
    ncols: int | None
    mininterval: float | None
    maxinterval: float | None
    miniters: float | None
    ascii: bool | str | None
    disable: bool
    unit: str
    unit_scale: bool | int | float
    dynamic_ncols: bool
    smoothing: float
    bar_format: str | None
    initail: int | float | None
    position: int | None
    postfix: Mapping[str, Any] | None
    unit_divisor: float
    write_bytes: bool
    lock_args: Iterable
    nrows: int | None
    colour: str | None
    "valid choices: [hex (#00ff00), BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE]"
    delay: float | None

class TqdmProxyKwargs(TqdmKwargs):
    @classmethod
    def to_tqdm_kwargs(cls, tqdm_proxy_kwargs: "TqdmProxyKwargs") -> TqdmKwargs:
        for k in cls.__annotations__:
            if k not in TqdmKwargs.__annotations__:
                tqdm_proxy_kwargs.pop(k, None)
        return tqdm_proxy_kwargs
    priority: int | float

class Tqdm(tqdm, Generic[_T]):

    pos: int | None
    cls_disable: bool = False

    @overload
    def _getattr(self, name: str, /): ...
    @overload
    def _getattr(self, name: str, default: Any, /): ...
    def _getattr(self, *args):
        return getattr(self, *args)

    def _setattr(self, name: str, value: Any):
        setattr(self, name, value)

    @overload
    def __init__(self, iterable: Iterable[_T] | None = None, pre_tqdm: object | None = None, **kwargs): ...
    @overload
    def __init__(self, iterable: Iterable[_T] | None = None, pre_tqdm: object | None = None, **kwargs: Unpack[TqdmKwargs]): ...
    def __init__(self, iterable: Iterable[_T] | None = None, pre_tqdm: object | None = None, **kwargs: Unpack[TqdmKwargs]):
        self._pre_tqdm = pre_tqdm
        super().__init__(iterable, **kwargs)

    def __iter__(self) -> Iterator[_T]:
        """Backward-compatibility to use: for x in tqdm(iterable)"""

        # Inlining instance variables as locals (speed optimisation)
        iterable = self.iterable

        # If the bar is disabled, then just walk the iterable
        # (note: keep this check outside the loop for performance)
        if self.disable:
            for obj in iterable:
                yield obj
            return

        mininterval = self.mininterval
        last_print_t = self.last_print_t
        last_print_n = self.last_print_n
        min_start_t = self.start_t + self.delay
        n = self.n
        time = self._time

        try:
            for obj in iterable:
                yield obj
                # Update and possibly print the progressbar.
                # Note: does not call self.update(1) for speed optimisation.
                n += 1

                if n - last_print_n >= self.miniters:
                    cur_t = time()
                    dt = cur_t - last_print_t
                    if dt >= mininterval and cur_t >= min_start_t:
                        self.update(n - last_print_n)
                        last_print_n = self.last_print_n
                        last_print_t = self.last_print_t
        finally:
            self.n = n
            # self.close()

    def display(self, msg: str | None = None, pos: int | None = None):
        if self.cls_disable: return
        super().display(msg, pos)

    def __bool__(self):
        return True

TqdmHostID = int
TqdmClientID = int
TqdmProxyID = int
"tqdm_proxy_id == 0 means the proxy is not assigned at tqdm_proces"

class TqdmRequest(TypedDict):
    handler_id: TqdmHostID | TqdmClientID
    proxy_id: TqdmProxyID
    op: str
    args: list[Any]
    kwargs: dict[str, Any]

TqdmResponse = Any

class TqdmProcess(Process):

    class _OrderedProgsItem(NamedTuple):
        priority: int | float
        datetime: datetime
        proxy_id: TqdmProxyID

    class _GT:
        def __gt__(self, other): return True
        def __ge__(self, other): return True
        def __lt__(self, other): return False
        def __le__(self, other): return False
        def __rgt__(self, other): return True
        def __rge__(self, other): return True
        def __rlt__(self, other): return False
        def __rle__(self, other): return False

    ORDERED_PROGS_SENTINEL = _GT()

    def __init__(
        self,
        to_host_q: "Queue[TqdmRequest]",
        to_client_qs: dict[TqdmHostID | TqdmClientID, "Queue[TqdmResponse]"],
        interval: float = 1/5
        ) -> None:

        super().__init__()

        self._progresses = dict[TqdmProxyID, Tqdm | object]()
        self._ordered_progs = deque[self._OrderedProgsItem]()
        self._loop_pipe: deque[TqdmRequest] = deque()
        self._loop_lock: Lock = _Lock()
        self._stop_secondary_loop: bool = False
        self._interval: float = interval
        self._position: int = 0

        self.to_host_q = to_host_q
        self.to_client_qs = to_client_qs

    def run(self):

        (primary_loop := Thread(target=self.primary_execute)).start()
        (secondary_loop := Thread(target=self.secondary_execute)).start()

        primary_loop.join()
        secondary_loop.join()

        for progress in self._progresses.values():
            if isinstance(progress, Tqdm):
                progress.close()
        self._progresses.clear()

    def primary_execute(self):

        try:

            while True:

                request = self.to_host_q.get()
                response = None
                op = request["op"]

                with self._loop_lock:

                    # non proxy operate
                    if op == "EXIT":
                        break
                    elif op == "write":
                        response = Tqdm.write(*request["args"], request["kwargs"])

                    # proxy operate
                    elif op == "tqdm":
                        pre_tqdm = object()
                        proxy_id = id(pre_tqdm)
                        request["proxy_id"] = proxy_id
                        self._progresses[proxy_id] = pre_tqdm
                        self._loop_pipe.append(request)
                        response = proxy_id

                    elif op in ("update", "clear", "reset", "display", "refresh", "close"):
                        self._loop_pipe.append(request)

                    elif op == "close":
                        self._loop_pipe.append(request)

                    else:
                        if isinstance(progress := self._progresses.get(proxy_id), Tqdm):
                            response = progress._getattr(op)(*request["args"], **request["kwargs"])
                        else:
                            self._loop_pipe.append(request)

                    self.to_client_qs[request["handler_id"]].put(response)

        except BaseException as e:
            traceback.print_exc()
            raise e

        finally:
            self._stop_secondary_loop = True
            return

    def secondary_execute(self):

        created_progs = list[self._OrderedProgsItem]()
        next_progs = deque[self._OrderedProgsItem]()
        closed_proxies = list[TqdmProxyID]()

        try:

            while True:

                with self._loop_lock:

                    Tqdm.cls_disable = False

                    while self._loop_pipe:

                        request = self._loop_pipe.popleft()
                        op = request["op"]
                        proxy_id = request["proxy_id"]

                        if op == "tqdm":

                            tqdm_priority: int | float = request["kwargs"].pop("priority", float("inf"))
                            self._progresses[proxy_id] = Tqdm(*request["args"], **request["kwargs"], pre_tqdm=self._progresses[proxy_id])
                            heapq.heappush(created_progs, self._OrderedProgsItem(tqdm_priority, datetime.now(), proxy_id))

                        elif op == "close":

                            closed_proxies.append(proxy_id)

                            if isinstance(progress := self._progresses.pop(proxy_id, None), Tqdm):
                                progress.close()

                        # elif op in ("update", "clear", "reset", "display", "refresh"):
                        else:

                            if isinstance(progress := self._progresses.get(proxy_id), Tqdm):
                                progress._getattr(op)(*request["args"], **request["kwargs"])

                    ordered_p = self._ordered_progs.popleft() if self._ordered_progs else self.ORDERED_PROGS_SENTINEL
                    created_p = heapq.heappop(created_progs) if created_progs else self.ORDERED_PROGS_SENTINEL

                    while ordered_p != self.ORDERED_PROGS_SENTINEL or created_p != self.ORDERED_PROGS_SENTINEL:

                        if ordered_p <= created_p:
                            item = ordered_p
                            ordered_p = self._ordered_progs.popleft() if self._ordered_progs else self.ORDERED_PROGS_SENTINEL

                        else:
                            item = created_p
                            created_p = heapq.heappop(created_progs) if created_progs else self.ORDERED_PROGS_SENTINEL

                        if TYPE_CHECKING and isinstance(item, self._GT): continue

                        if item.proxy_id not in closed_proxies:
                            next_progs.append(item)

                    order = -1
                    for item in next_progs:
                        if isinstance(progress := self._progresses.get(item.proxy_id, None), Tqdm):
                            progress.pos = (order := order + 1)
                            progress.refresh()

                    Tqdm.cls_disable = True

                    # self._ordered_progs and created_progs are empty

                    self._position = order + 1
                    self._ordered_progs, next_progs = next_progs, self._ordered_progs # swap
                    closed_proxies.clear()

                if self._stop_secondary_loop: break

                time.sleep(self._interval)

        except BaseException as e:
            traceback.print_exc()
            raise e

        finally:
            self.to_host_q.put(TqdmRequest(op="EXIT"))
            return

class TqdmSingle:
    @overload
    @classmethod
    def tqdm(cls, iterable: Iterable[_T], **tqdm_proxy_kwargs): ...
    @overload
    @classmethod
    def tqdm(cls, iterable: Iterable[_T], **tqdm_proxy_kwargs: Unpack[TqdmProxyKwargs]): ...
    @classmethod
    def tqdm(cls, iterable: Iterable[_T], **tqdm_proxy_kwargs: Unpack[TqdmProxyKwargs]):
        tqdm_kwargs = TqdmProxyKwargs.to_tqdm_kwargs(tqdm_proxy_kwargs)
        total = tqdm_kwargs.get("total") or (isinstance(iterable, Sized) and len(iterable)) or None
        return Tqdm(iterable, **(tqdm_kwargs | {"total": total}))
    @classmethod
    def write(cls, s: str, file: TextIO | None = None, end: str = "\n"):
        Tqdm.write(s, file, end)

class TqdmHost:

    class _State(TypedDict):
        _id: TqdmHostID
        to_host_q: "Queue[TqdmRequest]"
        to_client_qs: dict[TqdmHostID | TqdmClientID, "Queue[TqdmResponse]"]

    def __init__(self, sync_manager: SyncManager | None = None, tqdm_interval: float = 1/5):

        if parent_process() is not None: return

        if sync_manager:
            self.sync_manager = sync_manager # NOT Picklable
        else:
            self.sync_manager = SyncManager()

        if self.sync_manager._state.value <= 0: # multiprocessing.managers.State.INITIAL
            self.sync_manager.start()

        self._id = id(self)
        self.to_host_q: Queue[TqdmRequest] = self.sync_manager.Queue()
        self.to_client_q: Queue[TqdmResponse] = self.sync_manager.Queue()
        self.to_client_qs: dict[TqdmClientID, Queue[TqdmResponse]] = self.sync_manager.dict({
            self._id: self.to_client_q
        })
        self._lock: Lock = _Lock()

        self.tqdm_process = TqdmProcess(self.to_host_q, self.to_client_qs) # NOT Picklable
        self.tqdm_process.start()

    def __getstate__(self) -> _State:
        return self._State(
            _id=self._id,
            to_host_q=self.to_host_q,
            to_client_qs=self.to_client_qs
        )

    def __setstate__(self, state: _State):
        self._id = state["_id"]
        self.to_host_q = state["to_host_q"]
        self.to_client_qs = state["to_client_qs"]

    def client(self):
        return TqdmClient(self)

    @overload
    def tqdm(self, iterable: Iterable[_T], **tqdm_proxy_kwargs) -> "TqdmProxy[_T]": ...
    @overload
    def tqdm(self, iterable: Iterable[_T], **tqdm_proxy_kwargs: Unpack[TqdmProxyKwargs]) -> "TqdmProxy[_T]": ...
    def tqdm(self, iterable: Iterable[_T], **tqdm_proxy_kwargs: Unpack[TqdmProxyKwargs]):
        return TqdmProxy[_T](self, None, iterable, tqdm_proxy_kwargs)

    def __del__(self):

        if parent_process() is None:
            self.to_host_q.put(TqdmRequest(op="EXIT"))
            self.tqdm_process.join()

    def get_sync_manager(self):
        if parent_process() is None:
            return self.sync_manager
        else:
            raise RuntimeError

class TqdmClient:

    class _State(TypedDict):
        _id: TqdmClientID
        _host: TqdmHost
        to_host_q: "Queue[TqdmRequest]"
        to_client_q: "Queue[TqdmResponse]"

    def __init__(self, host: TqdmHost):

        self._id = id(self)
        self._host = host
        self.to_host_q = host.to_host_q
        self.to_client_q: Queue[TqdmResponse] = host.sync_manager.Queue()
        self._lock: Lock = _Lock()
        host.to_client_qs[self._id] = self.to_client_q

    def __getstate__(self):
        return self._State(
            _id=self._id,
            _host=self._host,
            to_host_q=self.to_host_q,
            to_client_q=self.to_client_q
        )

    def __setstate__(self, state: _State):
        self._id = state["_id"]
        self._host = state["_host"]
        self.to_host_q = state["to_host_q"]
        self.to_client_q = state["to_client_q"]
        self._lock = _Lock()

    @overload
    def tqdm(self, iterable: Iterable[_T], **tqdm_proxy_kwargs) -> "TqdmProxy[_T]": ...
    @overload
    def tqdm(self, iterable: Iterable[_T], **tqdm_proxy_kwargs: Unpack[TqdmProxyKwargs]) -> "TqdmProxy[_T]": ...
    def tqdm(self, iterable: Iterable[_T], **tqdm_proxy_kwargs: Unpack[TqdmProxyKwargs]):
        return TqdmProxy[_T](self._host, self, iterable, tqdm_proxy_kwargs)

    def write(self, s: str, file: TextIO | None = None, end: str = "\n"):

        with self._lock:

            request = TqdmRequest(
                handler_id = self._id,
                proxy_id = 0,
                op = "write", args = [s, file, end], kwargs = {}
            )
            self.to_host_q.put(request)
            self.to_client_q.get()

    def __del__(self):
        del self._host

class TqdmProxy(Generic[_T]):

    _id: TqdmProxyID = 0

    def _call(self, op: str, args: Sequence[Any] = (), kwargs: Mapping[str, Any] = {}):

        handler = self._client or self._host

        with handler._lock:

            request = TqdmRequest(
                handler_id = handler._id,
                proxy_id = self._id,
                op = op, args = list(args), kwargs = dict(kwargs)
            )
            handler.to_host_q.put(request)
            response = handler.to_client_q.get()

        return response

    def __init__(self, host: TqdmHost, client: TqdmClient | None, iterable: Iterable[_T], tqdm_proxy_kwargs: TqdmProxyKwargs):

        self._host: TqdmHost = host
        self._client: TqdmClient | None = client

        self.iterable: Iterable[_T] | reversed[_T] = iterable
        self.total: float | int | None = (
            total if isinstance(total := tqdm_proxy_kwargs.get("total"), int | float) else
            len(iterable) if isinstance(iterable, Sized) else
            None
        )

        self._id: TqdmProxyID = self._call("tqdm", kwargs = tqdm_proxy_kwargs | {"total": self.total})

    def __getattr__(self, name: str):
        return self._call("_getattr", (name,))

    def __bool__(self):
        if self.total is not None:
            return bool(self.total)
        return bool(self.iterable)

    def __len__(self):
        return (
            len(self.iterable) if isinstance(self.iterable, Sized) else
            int(self.total)
        )

    def __reversed__(self):
        self.iterable = reversed(self.iterable)
        return self.__iter__()

    def __contains__(self, item: Any):
        return item in self.iterable if isinstance(self.iterable, Container) else item in self.__iter__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type: type[Exception], exc_value: Exception, traceback: TracebackType):
        self.close()

    def __del__(self):
        self.close()
        del self._client
        del self._host

    def __str__(self) -> str:
        return self._call("__str__")

    @property
    def _comparable(self) -> int:
        return self._call("_getattr", ("_comparable",))

    def __hash__(self):
        return id(self)

    def __iter__(self):

        for item in self.iterable:
            yield item
            self.update()

    def write(self, s: str, file: TextIO | None, end: str = "\n"):
        self._call("write", (s, file, end))

    def update(self, n: int = 1):
        self._call("update", (n,))

    def close(self):
        self._call("close")

    def clear(self):
        self._call("clear")

    def refresh(self):
        self._call("refresh")

    def unpause(self):
        self._call("unpause")

    def reset(self, total: float | None):
        self._call("reset", (total,))

    def set_description(self, desc: str | None = None, refresh: bool = True):
        self._call("set_description", (desc, ))

    def set_description_str(self, desc: str | None, refresh: bool = True):
        self._call("set_description_str", (desc, ))

    def set_postfix(self, orderd_dict: dict | None = None, refresh: bool = True, **kwargs: Any):
        self._call("set_postfix", (orderd_dict,), kwargs)

    def set_postfix_str(self, s: str = "", refresh: bool = True):
        self._call("set_postfix_str", (s,))

    @property
    def format_dict(self) -> dict[str, Any]:
        return self._call("_getattr", ("format_dict",))

    def display(self, msg: str | None = None, pos: int | None = None):
        self._call("display", (msg, pos))

    @property
    def colour(self) -> str | None:
        return self._call("_getattr", args=("colour",))
    @colour.setter
    def colour(self, value: str | None):
        self._call("_setattr", ("colour", value))

    @property
    def pos(self) -> int | None:
        return self._call("_getattr", ("pos",))
    @pos.setter
    def pos(self, value: int | None):
        self._call("_setattr", ("pos", value))
