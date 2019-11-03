import numpy as np

from abc import ABC, abstractmethod

"""
Base class for other modulator objects
Also contains useful helper functions as static methods
"""
class Modulator(ABC):
    @staticmethod
    def generate_timearray(fs, sample_count):
        dt=1/fs
        return np.arange(0,dt*sample_count,dt)
    @staticmethod
    def samples_per_symbol(fs, baud):
        return fs/baud

    @abstractmethod
    def modulate(self, data):
        raise NotImplementedError
    @abstractmethod
    def demodulate(self, time_array, datastream):
        raise NotImplementedError
