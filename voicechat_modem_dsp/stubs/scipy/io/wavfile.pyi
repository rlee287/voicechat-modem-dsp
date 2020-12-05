from typing import Any, IO, Union, Tuple

from numpy import ndarray

def read(filename: Union[str, IO[Any]], mmap: bool=...) \
    -> Tuple[int, ndarray]: ...
def write(filename: Union[str, IO[Any]], rate: int, data: ndarray) -> None: ...