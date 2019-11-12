from .modulator_base import Modulator

from . import modulator_utils

import numpy as np

class ASKModulator(Modulator):
    def __init__(self, fs, carrier, amp_list, baud):
        if baud>=0.5*carrier:
            raise ValueError("Baud is too high to be modulated "+
                             "using carrier frequency")
        if fs<=2*carrier:
            raise ValueError("Carrier frequency is too high for sampling rate")
        if any((x>1 or x<0.1 for x in amp_list)):
            raise ValueError("Invalid amplitudes given")
        self.fs=fs
        self.amp_list=dict(enumerate(amp_list))
        self.baud=baud
    
    def modulate(self, data):
        samples_symbol=modulator_utils.samples_per_symbol(self.fs, self.baud)

        amplitude_data=[0,0]+[amp_list[datum] for datum in data]+[0,0]
        time_array=Modulator.generate_time_array(self.fs,len(amplitude_data)*samples_symbol)
        interpolated_amplitude=np.interp(
            np.linspace(0,int(len(data)*2),len(data),endpoint=False),
            range(len(amplitude_data)),amplitude_data)


    def demodulate(self, time_array, datastream):
        raise NotImplementedError