from numpy import ndarray

from abc import ABC, abstractmethod

from typing import Sequence

class BaseModulator(ABC):
    """
    Base class with helper functions for other modulator objects
    """
    # norm.isf(1/(2*2^8))
    sigma_mult_t=2.89
    # norm.isf(0.0001)
    sigma_mult_f=3.72
    fs=-1 #type: float

    @abstractmethod
    def modulate(self, datastream: Sequence[int]) -> ndarray:
        """Modulates the datastream into a signal for transmission"""
        raise NotImplementedError
    @abstractmethod
    def demodulate(self, modulated_data: ndarray) -> Sequence[int]:
        """Demodulates a signal into a datastream"""
        raise NotImplementedError
