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

from .mp import MP, MediaPipeHolisticOptions
from .progress import TqdmKwargs, Tqdm

_T = TypeVar("_T")
_P = ParamSpec("_P")
PROGRESS_DESC_PREFIX = "{:<16}"

class SharedDict(TypedDict):
    tqdm_pos_stock: list[int]
    sigint_event: Event

class MultiProcessDict(TypedDict):
    manager: Manager
    shared: SharedDict
    pool: ProcessPoolExecutor

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
        self.print(self.LEVEL[level], end="", file=file)
        self.print(*values, sep=sep, end="", file=file)
        self.print(self.LEVEL["reset"], sep="", end=end, file=file, flush=flush)
    def info(self, *args, **kwargs): return self.message('info'*args, **kwargs)
    def warning(self, *args, **kwargs): return self.message('warning'*args, **kwargs)
    def error(self, *args, **kwargs): return self.message('error', *args, **kwargs)

class AppBase:

    tqdm_position: int | None = None

    def __init__(
        self,
        holistic_options: MediaPipeHolisticOptions | None = None
        ):

        self.mp = MP(
            detect_targets = ["left_hand", "right_hand", "pose"],
            holistic_options = holistic_options
        )
    
    def run(self, *args, **kwargs):
        raise NotImplementedError

_AB = TypeVar("_AB", bound=AppBase)

class AppWorkerThread(Thread, Generic[_AB]):

    app_process: _AB
    sigint_event: Event
    rlock: RLock

    @classmethod
    def get_thread(cls) -> Self:
        return main_thread()

class AppExecutor(Generic[_AB]):

    app_type: type[_AB]
    "you must override this variable, nor raise NameError"
    
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
    def _signle_init(cls, tqdm_lock: RLock, io_rock: RLock):

        Tqdm.set_lock(tqdm_lock)

        thread = AppWorkerThread[_AB].get_thread()
        thread.app_process = cls.app_type()
        thread.app_process.tqdm_position = 0
        thread.rlock = io_rock
    
    @classmethod
    def _multi_init(cls, tqdm_lock: RLock, io_lock: RLock, shared: SharedDict):

        warnings.filterwarnings("ignore", category=UserWarning)

        Tqdm.set_lock(tqdm_lock)

        thread = AppWorkerThread[_AB].get_thread()
        thread.app_process = cls.app_type()
        thread.app_process.tqdm_position = shared["tqdm_pos_stock"].pop()
        thread.sigint_event = shared["sigint_event"]
        thread.rlock = io_lock
        signal.signal(signal.SIGINT, cls._sigint_handler(thread))

    def __init__(self, cpu: int | None):

        self.tqdm_lock = _RLock()
        self.io_lock = _RLock()
        Tqdm.set_lock(self.tqdm_lock)

        if cpu is None:

            self.tqdm_pos = 1
            self.multi_process_dict = self._signle_init(self.tqdm_lock, self.io_lock)
            self._map_func = map

        else:

            self.tqdm_pos = cpu
            self.multi_process_dict = MultiProcessDict({
                "manager": (manager := _Manager()),
                "shared": (shared := manager.dict({
                    "tqdm_pos_stock": manager.list(reversed(range(cpu))),
                    "sigint_event":  manager.Event()
                })),
                "pool": (pool := ProcessPoolExecutor(
                    max_workers = cpu,
                    initializer = self._multi_init,
                    initargs = (self.tqdm_lock, self.io_lock, shared)
                ))
            })
            self._map_func = pool.map

    @staticmethod
    def _map_job(args_kwargs: tuple[Iterable[Any], Mapping[str, Any]]) -> Any:

        try: return AppWorkerThread[_AB].get_thread().app_process.run(*args_kwargs[0], **args_kwargs[1])

        except process.BrokenProcessPool: pass
        except InvalidStateError: pass
    
    def execute(
        self,
        args_kwargs_iter: Iterable[tuple[Iterable[Any], Mapping[str, Any]]],
        tqdm_kwargs: TqdmKwargs = {}
        ):

        (sigint_manager := Thread(target=self._sigint_manager)).start()

        executor = self._map_func(self._map_job, args_kwargs_iter)

        progress = Tqdm(
            executor,
            **({
                "total": len(args_kwargs_iter) if isinstance(args_kwargs_iter, Sized) else None,
                "desc": f'\033[46m{PROGRESS_DESC_PREFIX.format("Processing...")}\033[0m',
                "bar_format": "{desc}: {percentage:6.2f}%{l_bar}{bar}{r_bar}\033[0J",
                "colour": "cyan",
                "position": self.tqdm_pos,
                "mininterval": 1/15,
                "maxinterval": 1/10
            } | tqdm_kwargs)
        )

        exception: Exception | None = None

        try:
            results = list(progress)
        
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

            progress.pos = 0
            progress.update(0)
            progress.close()

            if exception is not None:
                print(file=sys.stderr)
                raise exception
