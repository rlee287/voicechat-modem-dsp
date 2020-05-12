from .modulator_base import BaseModulator

from . import modulator_utils
from .modulator_utils import ModulationIntegrityWarning

import numpy as np
from scipy import signal
from scipy.cluster.vq import vq

import warnings

class ASKModulator(BaseModulator):
    def __init__(self, fs, carrier, amp_list, baud):
        if carrier<=0:
            raise ValueError("Frequency of carrier must be positive")
        if baud>=0.5*carrier:
            raise ValueError("Baud is too high to be modulated "+
                             "using carrier frequency")
        # Nyquist limit
        if carrier>=0.5*fs:
            raise ValueError("Carrier frequency is too high for sampling rate")
        if any((x>1 or x<=0 for x in amp_list)):
            raise ValueError("Invalid amplitudes given")

        self.fs=fs
        self.amp_list=dict(enumerate(amp_list))
        self.carrier_freq=carrier
        self.baud=baud
        # Nyquist aliased 2*carrier=carrier
        if carrier>=(1/3)*fs:
            warnings.warn("Carrier frequency is too high to guarantee "
                          "proper lowpass reconstruction",
                          ModulationIntegrityWarning)
        if any(x<0.1 for x in amp_list):
            warnings.warn("Some amplitudes may be too low "
                          "to be distinguishable from background noise",
                          ModulationIntegrityWarning)
        if any(dx<=0.05 for dx in np.diff(sorted(amp_list))):
            warnings.warn("Amplitudes may be too close "
                          "to be distinguishable from each other",
                          ModulationIntegrityWarning)
        # TODO: additional warnings relating to filter overshoot and the like
    
    @property
    def _calculate_sigma(self):
        #sigma_t = w/4k, at most half of the pulse is smoothed away
        gaussian_sigma_t=(1/self.baud)/(4*BaseModulator.sigma_mult_t)
        # Ensure dropoff at halfway to doubled carrier frequency is -80dB
        # This is not the same as carrier_freq because Nyquist reflections
        doubled_carrier_refl=min(
            2*self.carrier_freq,self.fs-2*self.carrier_freq)
        halfway_thresh=0.5*doubled_carrier_refl
        gaussian_sigma_f=BaseModulator.sigma_mult_f/(2*np.pi*halfway_thresh)
        return min(gaussian_sigma_t,gaussian_sigma_f)

    def modulate(self, datastream):
        samples_per_symbol=modulator_utils.samples_per_symbol(self.fs,self.baud)
        gaussian_sigma=self._calculate_sigma
        gaussian_window=modulator_utils.gaussian_window(self.fs,gaussian_sigma)

        # Map datastream to amplitudes and pad with 0 on both ends
        amplitude_data = np.pad([self.amp_list[datum] for datum in datastream],
            1,mode="constant",constant_values=0)

        # Upsample amplitude to actual sampling rate
        interp_sample_count=int(np.ceil(
            len(amplitude_data)*samples_per_symbol))
        time_array=modulator_utils.generate_timearray(
            self.fs,interp_sample_count)
        interpolated_amplitude=modulator_utils.previous_resample_interpolate(
            time_array, self.baud, amplitude_data)
        # Smooth amplitudes with Gaussian kernel
        shaped_amplitude=signal.convolve(interpolated_amplitude,gaussian_window,
            "same",method="fft")

        # Multiply amplitudes by carrier
        return shaped_amplitude * \
            np.cos(2*np.pi*self.carrier_freq*time_array)

    def demodulate(self, modulated_data):
        samples_per_symbol=modulator_utils.samples_per_symbol(self.fs,self.baud)
        # Use complex exponential to allow for phase drift
        time_array=modulator_utils.generate_timearray(
            self.fs,len(modulated_data))
        demod_amplitude=2*modulated_data*np.exp(2*np.pi*1j*self.carrier_freq*time_array)

        # Compute filter boundaries
        # Lowend is half the baud (i.e. the fundamental of the data)
        # Highend blocks fundamental of data and optionally voice
        # TODO: improve this part
        carrier_refl=min(2*self.carrier_freq,self.fs-2*self.carrier_freq)
        filter_lowend=0.5*self.baud
        filter_highend=carrier_refl-filter_lowend
        if carrier_refl-4000>self.carrier_freq:
            filter_highend=carrier_refl-4000

        # Construct FIR filter, filter demodulated signal, and discard phase
        fir_filt=modulator_utils.lowpass_fir_filter(self.fs, filter_lowend, filter_highend)
        filt_delay=(len(fir_filt)-1)//2
        # First append filt_delay number of zeros to incoming signal
        demod_amplitude=np.pad(demod_amplitude,(0,filt_delay))
        filtered_demod_amplitude=np.abs(signal.lfilter(fir_filt,1,demod_amplitude))

        # Extract the original amplitudes via averaging of plateau

        # Round to account for floating point weirdness
        interval_count=int(np.round(
            len(modulated_data)/samples_per_symbol))
        interval_offset=filt_delay
        list_amplitudes=list()

        transition_width=BaseModulator.sigma_mult_t*self._calculate_sigma
        # Convert above time width into sample point width
        transition_width*=self.fs

        for i in range(interval_count):
            interval_begin=interval_offset+i*samples_per_symbol
            # Perform min in order to account for floating point weirdness
            interval_end=min(interval_begin+samples_per_symbol,
                len(modulated_data)-1)

            # Shrink interval by previously calculated transition width
            # Skip doing so for first and last sample
            if i!=0:
                interval_begin+=transition_width
            if i!=interval_count-1:
                interval_end-=transition_width
            # Find the amplitude by averaging
            list_amplitudes.append(modulator_utils.average_interval_data(filtered_demod_amplitude, interval_begin, interval_end))

        # Convert amplitude observations and mapping into vq arguments
        # Insert the null symbol 0 to account for beginning and end
        list_amplitudes=[[amplitude] for amplitude in list_amplitudes]
        code_book=[self.amp_list[i] for i in range(len(self.amp_list))]
        code_book.insert(0,0.0)
        code_book=[[obs] for obs in code_book]

        # Map averages to amplitude points
        vector_cluster=vq(list_amplitudes,code_book)
        # Subtract data points by 1 and remove 0 padding
        # Neat side effect: -1 is an invalid data point
        datastream=vector_cluster[0]-1
        if (datastream[0]!=-1 or datastream[-1]!=-1
                or any(datastream[1:-1]==-1)):
            warnings.warn("Corrupted datastream detected while demodulating",
                ModulationIntegrityWarning)
        return datastream[1:-1]
