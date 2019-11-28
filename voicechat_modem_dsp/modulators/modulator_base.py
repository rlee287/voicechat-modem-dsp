import numpy as np

from abc import ABC, abstractmethod

"""
Base class for other modulator objects
Also contains useful helper functions as static methods
"""
class Modulator(ABC):
    @abstractmethod
    def modulate(self, datastream):
        raise NotImplementedError
    @abstractmethod
    def demodulate(self, modulated_data):
        raise NotImplementedError
