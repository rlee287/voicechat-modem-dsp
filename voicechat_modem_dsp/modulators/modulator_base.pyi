# Stubs for modulators.modulator_base (Python 3)

import abc
from abc import ABC, abstractmethod
from typing import Any

class Modulator(ABC, metaclass=abc.ABCMeta):
    @staticmethod
    def generate_timearray(dt: float, sample_count: int): ...
    @staticmethod
    def samples_per_symbol(dt: float, baud: float): ...
    @abstractmethod
    def modulate(self, data: Any) -> Any: ...
    @abstractmethod
    def demodulate(self, time_array: Any, datastream: Any) -> Any: ...
