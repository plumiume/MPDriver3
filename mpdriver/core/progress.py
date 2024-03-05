from typing import TypedDict, TextIO, Mapping, Iterable, Iterator, Unpack, Any, TypeVar, Generic
from tqdm import tqdm

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
    delay: float | None

class Tqdm(tqdm, Generic[_T]):
    def __init__(self, iterable: Iterable[_T], **kwargs: Unpack[TqdmKwargs]):
        return super().__init__(iterable, **kwargs)
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
