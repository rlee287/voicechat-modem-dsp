from .modulator_base import BaseModulator

from . import modulator_utils
from .modulator_utils import ModulationIntegrityWarning

import numpy as np
from scipy import signal
import scipy.integrate
from scipy.cluster.vq import vq

import warnings

class FSKModulator(BaseModulator):
    def __init__(self, fs, amplitude, freq_list, baud):
        if min(freq_list)<=0:
            raise ValueError("Invalid frequencies given")
        if baud>min(freq_list):
            raise ValueError("Baud is too high to be modulated "+
                             "using given frequencies")
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
        # Frequency spacing for DFT
        dft_min_freq_gap=0.5*fs/(fs/baud)
        if any(dx<=dft_min_freq_gap for dx in np.diff(sorted(freq_list))):
            warnings.warn("Frequencies may be too close "
                          "to be distinguishable from one another",
                          ModulationIntegrityWarning)
        # TODO: additional warnings relating to Goertzel resolution, etc.

    @property
    def _calculate_sigma(self):
        #sigma_t = w/4k, at most half of the pulse is smoothed away
        gaussian_sigma_t=(1/self.baud)/(4*BaseModulator.sigma_mult_t)
        # At most 1/4 of the highest frequency cycle is smoothed away
        # TODO: test possibilities that make sense for FSK
        gaussian_sigma_f=0.25*(2*np.pi/max(self.freq_list.values()))/ \
            BaseModulator.sigma_mult_t
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

        # Construct smoothed frequency mask
        # TODO: be smarter about only convolving the edges
        amplitude_mask=np.asarray([0]+[self.amplitude]*len(datastream)+[0])
        interpolated_amplitude=modulator_utils.previous_resample_interpolate(
            time_array,self.baud,amplitude_mask)
        shaped_amplitude=signal.convolve(interpolated_amplitude,gaussian_window,
            "same",method="fft")

        # Frequency is the derivative of phase
        phase_array=scipy.integrate.cumtrapz(
            interpolated_frequency,time_array,initial=0)
        phase_array*=2*np.pi

        return shaped_amplitude*np.cos(phase_array)

    def demodulate(self, modulated_data):
        samples_per_symbol=modulator_utils.samples_per_symbol(self.fs,self.baud)
        goertzel_filters={index: modulator_utils.goertzel_iir(freq,self.fs)
            for index, freq in self.freq_list.items()}
        list_frequencies=[self.freq_list[i] for i in range(len(self.freq_list))]
        
        interval_count=int(np.round(
            len(modulated_data)/samples_per_symbol))
        goertzel_results=list()

        transition_width=BaseModulator.sigma_mult_t*self._calculate_sigma
        # Convert above time width into sample point width
        transition_width*=self.fs

        for i in range(interval_count):
            interval_begin=i*samples_per_symbol
            # Perform min in order to account for floating point weirdness
            interval_end=min(interval_begin+samples_per_symbol,
                len(modulated_data)-1)

            # Shrink interval by previously calculated transition width
            # Skip doing so for first and last sample
            if i==0 or i==interval_count-2:
                interval_end-=transition_width
            if i==1 or i==interval_count-1:
                interval_begin+=transition_width
            # Round transition boundaries to get integer indexes
            # TODO: find elegant way to handle noninteger interval bounds
            interval_begin=int(np.round(interval_begin))
            interval_end=int(np.round(interval_end))
            # Find the frequency using Goertzel "filter"
            goertzel_result=list()
            for index in range(len(self.freq_list)):
                val=signal.lfilter(*goertzel_filters[index],
                    modulated_data[interval_begin:interval_end+1])[-1]
                val=2*np.abs(val)/(interval_end-interval_begin)
                goertzel_result.append(val)

            goertzel_results.append(goertzel_result)

        codebook_vectors=self.amplitude*np.identity(len(self.freq_list))
        codebook_vectors=np.insert(codebook_vectors,
            0,[0]*len(self.freq_list),axis=0)
        vector_cluster=vq(goertzel_results, codebook_vectors)

        # Subtract data points by 1 and remove 0 padding
        # Neat side effect: -1 is an invalid data point
        datastream=vector_cluster[0]-1
        if (datastream[0]!=-1 or datastream[-1]!=-1
                or any(datastream[1:-1]==-1)):
            warnings.warn("Corrupted datastream detected while demodulating",
                ModulationIntegrityWarning)
        return datastream[1:-1]
