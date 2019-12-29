from numpy import ndarray

from abc import ABC, abstractmethod

from typing import Sequence

"""
Base class for other modulator objects
Also contains useful helper functions as static methods
"""
class Modulator(ABC):
    # norm.isf(1/(2*2^8))
    sigma_mult_t=2.89
    # norm.isf(0.0001)
    sigma_mult_f=3.72

    @abstractmethod
    def modulate(self, datastream: Sequence[int]) -> ndarray:
        raise NotImplementedError
    @abstractmethod
    def demodulate(self, modulated_data: ndarray) -> Sequence[int]:
        raise NotImplementedError
