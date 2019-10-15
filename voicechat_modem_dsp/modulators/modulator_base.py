import numpy as np

"""
Base class for other modulator objects
"""
class Modulator(object):
    @staticmethod
    def generate_timearray(dt, sample_count):
        return np.arange(0,dt*sample_count,dt)
    def modulate(self, data):
        raise NotImplementedError
    def demodulate(self, time_array, datastream):
        raise NotImplementedError
