from typing import MutableSequence, Union, Tuple, Callable

from numpy import ndarray

array_like=Union[float,MutableSequence[float],MutableSequence[int],ndarray]

# <class 'scipy.interpolate.interpolate.interp1d'>
def interp1d(x: array_like, y: array_like,
    kind: Union[str,int]=..., axis: int=...,
    copy: bool=..., bounds_error: bool=...,
    fill_value: Union[array_like,Tuple[array_like,array_like],str]=...,
    assume_sorted: bool=...) -> \
        Union[Callable[[float],float], Callable[[ndarray],ndarray]]: ...