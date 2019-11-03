# Stubs for modulators.modulator_base (Python 3)

import abc
from abc import ABC, abstractmethod
from typing import Any

class Modulator(ABC, metaclass=abc.ABCMeta):
    @staticmethod
    def generate_timearray(fs: float, sample_count: int): ...
    @staticmethod
    def samples_per_symbol(fs: float, baud: float) -> float: ...
    @abstractmethod
    def modulate(self, data: Any) -> Any: ...
    @abstractmethod
    def demodulate(self, time_array: Any, datastream: Any) -> Any: ...
