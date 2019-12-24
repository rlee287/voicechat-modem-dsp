from numpy import ndarray

from abc import ABC, abstractmethod

from typing import Sequence

"""
Base class for other modulator objects
Also contains useful helper functions as static methods
"""
class Modulator(ABC):
    @abstractmethod
    def modulate(self, datastream: Sequence[int]) -> ndarray:
        raise NotImplementedError
    @abstractmethod
    def demodulate(self, modulated_data: ndarray) -> Sequence[int]:
        raise NotImplementedError
