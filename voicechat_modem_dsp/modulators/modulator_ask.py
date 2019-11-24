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
        self.carrier_freq=carrier
        self.baud=baud
    
    def modulate(self, data):
        samples_symbol=modulator_utils.samples_per_symbol(self.fs, self.baud)
        #sigma_t = w/4k, explain later
        gaussian_sigma=(1/self.baud)/(4*2.5)
        gaussian_window=modulator_utils.compute_gaussian_window(self.fs,gaussian_sigma)

        amplitude_data=[0]+[self.amp_list[datum] for datum in data]+[0]
        interp_sample_count=np.ceil(len(amplitude_data)*samples_symbol)
        time_array=modulator_utils.generate_timearray(
            self.fs,interp_sample_count)

        interpolated_amplitude=modulator_utils.previous_resample_interpolate(
            time_array, self.baud, amplitude_data)
        shaped_amplitude=np.convolve(interpolated_amplitude,gaussian_window,
            "same")

        return (time_array,shaped_amplitude * \
            np.sin(2*np.pi*self.carrier_freq*time_array))

    def demodulate(self, time_array, datastream):
        raise NotImplementedError