import numpy as np

from abc import ABC, abstractmethod

"""
Base class for other modulator objects
Also contains useful helper functions as static methods
"""
class Modulator(ABC):
    @staticmethod
    def generate_timearray(dt, sample_count):
        return np.arange(0,dt*sample_count,dt)
    @staticmethod
    def samples_per_symbol(dt, baud):
        return (1/baud)/dt

    @abstractmethod
    def modulate(self, data):
        raise NotImplementedError
    @abstractmethod
    def demodulate(self, time_array, datastream):
        raise NotImplementedError
