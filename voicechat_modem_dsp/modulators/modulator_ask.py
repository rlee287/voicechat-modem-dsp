from .modulator_base import Modulator

from . import modulator_utils

import numpy as np
from scipy import signal

class ASKModulator(Modulator):
    # norm.isf(1/(2*2^8))
    sigma_mult_t=2.89
    # norm.isf(0.0001)
    sigma_mult_f=3.72

    def __init__(self, fs, carrier, amp_list, baud):
        if baud>=0.5*carrier:
            raise ValueError("Baud is too high to be modulated "+
                             "using carrier frequency")
        # TODO: set tighter bounds because of 2*carrier?
        if fs<=2*carrier:
            raise ValueError("Carrier frequency is too high for sampling rate")
        if any((x>1 or x<0.1 for x in amp_list)):
            raise ValueError("Invalid amplitudes given")
        self.fs=fs
        self.amp_list=dict(enumerate(amp_list))
        self.carrier_freq=carrier
        self.baud=baud
    
    @property
    def _calculate_sigma(self):
        #sigma_t = w/4k, explain later
        gaussian_sigma_t=(1/self.baud)/(4*ASKModulator.sigma_mult_t)
        #Ensure dropoff at carrier frequency is -80dB
        gaussian_sigma_f=ASKModulator.sigma_mult_f/(2*np.pi*self.carrier_freq)
        return min(gaussian_sigma_t,gaussian_sigma_f)
    
    @property
    def _samples_per_symbol(self):
        return modulator_utils.samples_per_symbol(self.fs,self.baud)
    
    def modulate(self, datastream):
        gaussian_sigma=self._calculate_sigma
        gaussian_window=modulator_utils.gaussian_window(self.fs,gaussian_sigma)
        amplitude_data = np.pad([self.amp_list[datum] for datum in datastream],
            1,mode="constant",constant_values=0)

        interp_sample_count=np.ceil(len(amplitude_data)*self._samples_per_symbol)
        time_array=modulator_utils.generate_timearray(
            self.fs,interp_sample_count)

        interpolated_amplitude=modulator_utils.previous_resample_interpolate(
            time_array, self.baud, amplitude_data)
        shaped_amplitude=signal.convolve(interpolated_amplitude,gaussian_window,
            "same",method="fft")

        return shaped_amplitude * \
            np.cos(2*np.pi*self.carrier_freq*time_array)

    def demodulate(self, modulated_data):
        # TODO: find an easier robust way to demodulate?
        time_array=modulator_utils.generate_timearray(
            self.fs,len(modulated_data))
        demod_amplitude=2*modulated_data*np.exp(2*np.pi*1j*self.carrier_freq*time_array)

        # Compute filter boundaries
        carrier_refl=min(2*self.carrier_freq,self.fs-2*self.carrier_freq)
        filter_lowend=0.5*self.baud
        filter_highend=carrier_refl-filter_lowend
        if carrier_refl-4000>self.carrier_freq:
            filter_highend=carrier_refl-4000

        fir_filt=modulator_utils.lowpass_fir_filter(self.fs, filter_lowend, filter_highend)
        filt_delay=(len(fir_filt)-1)//2
        interval_indexing=filt_delay
        while interval_indexing+self._samples_per_symbol<=(len(modulated_data)-1):
            pass #stuff
        filtered_demod_amplitude=signal.lfilter(fir_filt,1,demod_amplitude)
        return np.abs(filtered_demod_amplitude)