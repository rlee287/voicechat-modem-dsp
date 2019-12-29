from .modulator_base import Modulator

from . import modulator_utils
from .modulator_utils import ModulationIntegrityWarning

import numpy as np
from scipy import signal
import scipy.integrate

import warnings

class FSKModulator(Modulator):
    def __init__(self, fs, amplitude, freq_list, baud):
        if baud>min(freq_list):
            raise ValueError("Baud is too high to be modulated "+
                             "using given frequencies")
        if min(freq_list)<=0:
            raise ValueError("Invalid frequencies given")
        # Nyquist limit
        if max(freq_list)>=0.5*fs:
            raise ValueError("Maximum frequency is too high for sampling rate")
        if amplitude>1 or amplitude<=0:
            raise ValueError("Base amplitude must be positive and at most 1")

        self.fs=fs
        self.amplitude=amplitude
        self.freq_list=dict(enumerate(freq_list))
        self.baud=baud

        if amplitude<0.1:
            warnings.warn("Amplitude may be too small to allow "
                          "reliable reconstruction",ModulationIntegrityWarning)
        # TODO: additional warnings relating to Goertzel resolution, etc.

    @property
    def _calculate_sigma(self):
        #sigma_t = w/4k, at most half of the pulse is smoothed away
        gaussian_sigma_t=(1/self.baud)/(4*Modulator.sigma_mult_t)
        # TODO: test possibilities that make sense for FSK
        gaussian_sigma_f=(2*np.pi/max(self.freq_list.values()))/Modulator.sigma_mult_t
        return min(gaussian_sigma_t,gaussian_sigma_f)

    def modulate(self, datastream):
        samples_per_symbol=modulator_utils.samples_per_symbol(self.fs,self.baud)
        gaussian_sigma=self._calculate_sigma
        gaussian_window=modulator_utils.gaussian_window(self.fs,gaussian_sigma)

        # Map datastream to frequencies and pad on both ends
        # Exact padding does not matter because of amplitude shaping
        frequency_data = np.pad([self.freq_list[datum] for datum in datastream],
            1,mode="constant",constant_values=0)

        # Upsample frequency to actual sampling rate
        interp_sample_count=int(np.ceil(
            len(frequency_data)*samples_per_symbol))
        time_array=modulator_utils.generate_timearray(
            self.fs,interp_sample_count)
        interpolated_frequency=modulator_utils.previous_resample_interpolate(
            time_array, self.baud, frequency_data)
        # Smooth frequencies with Gaussian kernel
        shaped_frequency=signal.convolve(interpolated_frequency,gaussian_window,
            "same",method="fft")

        # Construct smoothed amplitude mask
        # TODO: be smarter about only convolving the edges
        amplitude_mask=np.asarray([0]+[self.amplitude]*len(datastream)+[0])
        interpolated_amplitude=modulator_utils.previous_resample_interpolate(
            time_array,self.baud,amplitude_mask)
        shaped_amplitude=signal.convolve(interpolated_amplitude,gaussian_window,
            "same",method="fft")

        # Frequency is the derivative of phase
        phase_array=scipy.integrate.cumtrapz(
            shaped_frequency,time_array,initial=0)%1
        phase_array*=2*np.pi

        return shaped_amplitude*np.cos(phase_array)

    def demodulate(self, modulated_data):
        raise NotImplementedError