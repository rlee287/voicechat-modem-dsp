import numpy as np

from abc import ABC, abstractmethod

"""
Base class for other modulator objects
"""
class Modulator(ABC):
    @staticmethod
    def generate_timearray(dt, sample_count):
        return np.arange(0,dt*sample_count,dt)
    @abstractmethod
    def modulate(self, data):
        raise NotImplementedError
    @abstractmethod
    def demodulate(self, time_array, datastream):
        raise NotImplementedError
