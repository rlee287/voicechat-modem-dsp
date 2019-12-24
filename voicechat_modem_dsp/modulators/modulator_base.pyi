# Stubs for modulators.modulator_base (Python 3)

import abc
from abc import ABC, abstractmethod
from typing import Any

class Modulator(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def modulate(self, datastream: Any) -> Any: ...
    @abstractmethod
    def demodulate(self, modulated_data: Any) -> Any: ...
