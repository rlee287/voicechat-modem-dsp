from typing import Any, List, Union, Optional, Tuple, Callable

from numpy import ndarray

from . import windows

# TODO: use ndarray instead?
floatpoint_t = Union[float, complex]

def firls(numtaps: int, bands: List[float], weight: List[float] = ...,
    nyq: float=..., fs: float=...) -> List[float]: ...
def freqz(b: List[floatpoint_t], a: List[floatpoint_t]=...,
    worN: Union[int,List[float]]=..., whole: bool=...,
    plot: Callable[[List[float],List[float]],Any]=...,
    fs: float=...) -> Tuple[List[float],List[floatpoint_t]]: ...