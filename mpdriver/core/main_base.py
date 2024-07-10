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

import sys
from typing import *
from types import FrameType
from itertools import *
import warnings
import signal
from threading import Thread, main_thread, Event
from multiprocessing.managers import SyncManager as Manager      # static analysis
from multiprocessing.synchronize import RLock                    # static analysis
from multiprocessing import Manager as _Manager, RLock as _RLock # actual import
from concurrent.futures import ProcessPoolExecutor, InvalidStateError, process

from .progress import TqdmKwargs, Tqdm, TqdmSingle, TqdmHost, TqdmClient

_T = TypeVar("_T")
_P = ParamSpec("_P")
PROGRESS_DESC_PREFIX = "{:<16}"

class PrintKwargs(TypedDict):
    sep: str | None
    end: str | None
    file: TextIO | None
    flush: bool

class Verbose:

    LEVEL: dict[Literal["info", "warning", "error", "reset", ""], str] = {
        ""        : "",
        "info"    :         "INFO    : ",
        "warning" : "\033[33mWARNING : ",
        "error"   : "\033[30mERROR   : ",
        "reset"   : "\033[0m"
    }

    def __init__(self, _v: bool):

        if _v:
            self.print = print
        else:
            self.print = lambda *args, **kwds: None

    def message(
        self,
        level: Literal["info", "warning", "error", ""],
        *values: object,
        sep: str | None = " ",
        end: str | None = "\n",
        file: TextIO | None = None,
        flush: bool = False
        ):

        if level == "error":
            p = print
        else:
            p = self.print

        p(self.LEVEL[level], end="", file=file)
        p(*values, sep=sep, end="", file=file)
        p(self.LEVEL["reset"], sep="", end=end, file=file, flush=flush)

    def info(self, *args: object, **kwargs: Unpack[PrintKwargs]): return self.message('info'*args, **kwargs)
    def warning(self, *args: object, **kwargs: Unpack[PrintKwargs]): return self.message('warning'*args, **kwargs)
    def error(self, *args: object, **kwargs: Unpack[PrintKwargs]): return self.message('error', *args, **kwargs)


class SharedDict(TypedDict): # For All Process
    tqdm_clients: list[TqdmClient]
    sigint_event: Event

class MultiProcessDict(TypedDict): # For Main Process
    manager: Manager
    tqdm_host: TqdmHost
    shared: SharedDict
    pool: ProcessPoolExecutor

class AppBase:

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError

_AB = TypeVar("_AB", bound=AppBase)

class AppWorkerThread(Thread, Generic[_AB]): # For Sub Process

    app_process: _AB
    tqdm_handler: TqdmSingle | TqdmClient
    sigint_event: Event
    rlock: RLock

    @classmethod
    def get_thread(cls) -> Self:
        return main_thread()

class AppExecutor(Generic[_AB]): # For Main Process

    app_type: type[_AB]

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "app_type"): raise NameError("if you want to create 'AppExecutor' child, must override 'app_type' variable.")
        return super().__init_subclass__()
    
    @staticmethod
    def _sigint_handler(thread: AppWorkerThread[_AB]):

        def handler(signum: int, frame: FrameType):
            thread.rlock.acquire()
            thread.sigint_event.set()

        return handler

    def _sigint_manager(self):

        if self.multi_process_dict is None: return

        shared = self.multi_process_dict["shared"]
        pool = self.multi_process_dict["pool"]

        shared["sigint_event"].wait()

        if pool._processes is None: return
        for p in pool._processes.values():
            if p.is_alive():
                p.kill()
    
    def _sigint_deleter(self):

        if self.multi_process_dict is None: return

        self.multi_process_dict["shared"]["sigint_event"].set()
    
    @classmethod
    def _signle_init(cls, io_rock: RLock, appbase_args: Iterable[Any] = (), appbase_kwargs: Mapping[str, Any] = {}):

        thread = AppWorkerThread[_AB].get_thread()
        thread.app_process = cls.app_type(*appbase_args, **appbase_kwargs)
        thread.rlock = io_rock
        thread.tqdm_handler = TqdmSingle
    
    @classmethod
    def _multi_init(cls, io_lock: RLock, shared: SharedDict, appbase_args: Iterable[Any] = (), appbase_kwargs: Mapping[str, Any] = {}):

        warnings.filterwarnings("ignore", category=UserWarning)

        thread = AppWorkerThread[_AB].get_thread()
        thread.app_process = cls.app_type(*appbase_args, **appbase_kwargs)
        thread.sigint_event = shared["sigint_event"]
        thread.rlock = io_lock
        thread.tqdm_handler = shared["tqdm_clients"].pop()
        signal.signal(signal.SIGINT, cls._sigint_handler(thread))

    def __init__(self, cpu: int | None = None, appbase_args: Iterable[Any] = (), appbase_kwargs: Mapping[str, Any] = {}):

        self.io_lock = _RLock()

        if cpu is None:

            self.multi_process_dict = self._signle_init(self.io_lock)
            self._map_func = map
            self._tqdm_func = TqdmSingle.tqdm

        else:

            self.multi_process_dict = MultiProcessDict({
                "manager": (manager := _Manager()),
                "tqdm_host": (tqdm_host := TqdmHost(manager)),
                "shared": (shared := manager.dict({
                    "tqdm_clients": manager.list([tqdm_host.client() for _ in range(cpu)]),
                    "sigint_event": manager.Event()
                })),
                "pool": (pool := ProcessPoolExecutor(
                    max_workers = cpu,
                    initializer = self._multi_init,
                    initargs = (self.io_lock, shared)
                ))
            })
            self._map_func = pool.map
            self._tqdm_func = tqdm_host.tqdm

    @staticmethod
    def _map_job(args_kwargs: tuple[Iterable[Any], Mapping[str, Any]]) -> Any:

        try: return AppWorkerThread[_AB].get_thread().app_process.run(*args_kwargs[0], **args_kwargs[1])

        except process.BrokenProcessPool: pass
        except InvalidStateError: pass
    
    def execute(
        self,
        args_kwargs_iter: Iterable[tuple[Iterable[Any], Mapping[str, Any]]],
        tqdm_kwargs: TqdmKwargs = {}
        ) -> list[Any]:

        (sigint_manager := Thread(target=self._sigint_manager)).start()

        executor = self._map_func(self._map_job, args_kwargs_iter)

        progress = self._tqdm_func(
            executor,
            **({
                "total": len(args_kwargs_iter) if isinstance(args_kwargs_iter, Sized) else None,
                "desc": f'\033[46m{PROGRESS_DESC_PREFIX.format("Processing...")}\033[0m',
                "bar_format": "{desc}: {percentage:6.2f}%|{bar}{r_bar}\033[0J",
                "colour": "cyan",
                "mininterval": 1/15,
                "maxinterval": 1/10,
                "priority": 1
            } | tqdm_kwargs)
        )

        exception: Exception | None = None
        result: list[Any] | None = None

        try:
            result = list(progress)
        
        except KeyboardInterrupt:
            progress.colour = "yellow"
            progress.set_description_str(f'\033[43m{PROGRESS_DESC_PREFIX.format("^C")}\033[0m')
        
        except Exception as e:
            progress.colour = "red"
            progress.set_description_str(f'\033[41m{PROGRESS_DESC_PREFIX.format("Aborted")}\033[0m')
            exception = e

        else: # Completed with no Error
            progress.colour = "green"
            progress.set_description_str(f'\033[42m{PROGRESS_DESC_PREFIX.format("Completed")}\033[0m')
        
        finally:

            self._sigint_deleter()
            sigint_manager.join()

            progress.close()

            if exception is not None:
                print(file=sys.stderr)
                raise exception

            return result
