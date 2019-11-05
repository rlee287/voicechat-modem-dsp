# Stubs for modulators.modulator_base (Python 3)

import abc
from abc import ABC, abstractmethod
from typing import Any

class Modulator(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def modulate(self, data: Any) -> Any: ...
    @abstractmethod
    def demodulate(self, time_array: Any, datastream: Any) -> Any: ...
