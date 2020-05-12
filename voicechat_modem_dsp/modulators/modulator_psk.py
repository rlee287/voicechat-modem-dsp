from .modulator_base import BaseModulator

from . import modulator_utils
from .modulator_utils import ModulationIntegrityWarning

import numpy as np
from scipy import signal
from scipy.cluster.vq import vq

import warnings

class PSKModulator(BaseModulator):
    def __init__(self, fs, carrier, amplitude, phase_list, baud):
        if carrier<=0:
            raise ValueError("Frequency of carrier must be positive")
        if baud>=0.5*carrier:
            raise ValueError("Baud is too high to be modulated "+
                             "using carrier frequency")
        # Nyquist limit
        if carrier>=0.5*fs:
            raise ValueError("Carrier frequency is too high for sampling rate")
        if any((x>=2*np.pi or x<0 for x in phase_list)):
            raise ValueError("Invalid phases given")

        if amplitude>1 or amplitude<=0:
            raise ValueError("Base amplitude must be positive and at most 1")

        self.amplitude=amplitude
        self.fs=fs
        self.phase_list=dict(enumerate(phase_list))
        self.carrier_freq=carrier
        self.baud=baud
        # Nyquist aliased 2*carrier=carrier
        if carrier>=(1/3)*fs:
            warnings.warn("Carrier frequency is too high to guarantee "
                          "proper lowpass reconstruction",
                          ModulationIntegrityWarning)
        if amplitude<0.1:
            warnings.warn("Amplitude may be too small to allow "
                          "reliable reconstruction",ModulationIntegrityWarning)
        if any(dx<=(0.05*2*np.pi) for dx in np.diff(sorted(phase_list))):
            warnings.warn("Phases may be too close "
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

        # Map datastream to phases and pad with 0 on both ends
        phase_data = np.pad([self.phase_list[datum] for datum in datastream],
            1,mode="constant",constant_values=0)

        # Upsample amplitude to actual sampling rate
        interp_sample_count=int(np.ceil(
            len(phase_data)*samples_per_symbol))
        time_array=modulator_utils.generate_timearray(
            self.fs,interp_sample_count)
        interpolated_phase=modulator_utils.previous_resample_interpolate(
            time_array, self.baud, phase_data)
        # Smooth phases with Gaussian kernel after mapping to complex plane
        interpolated_phase=np.exp(1j*interpolated_phase)
        shaped_phase=signal.convolve(interpolated_phase,gaussian_window,
            "same",method="fft")

        # Construct smoothed signal mask
        # TODO: be smarter about only convolving the edges
        amplitude_mask=np.asarray([0]+[self.amplitude]*len(datastream)+[0])
        interpolated_amplitude=modulator_utils.previous_resample_interpolate(
            time_array,self.baud,amplitude_mask)
        shaped_amplitude=signal.convolve(interpolated_amplitude,gaussian_window,
            "same",method="fft")

        shaped_phase*=shaped_amplitude

        # Multiply amplitudes by carrier
        return np.real(shaped_phase * 
            np.exp(2*np.pi*1j*self.carrier_freq*time_array))

    def demodulate(self, modulated_data):
        # TODO: copy this over to the QAM modulator
        # This is close enough to maybe allow object composition
        samples_per_symbol=modulator_utils.samples_per_symbol(self.fs,self.baud)
        time_array=modulator_utils.generate_timearray(
            self.fs,len(modulated_data))
        demod_signal=2*modulated_data*np.exp(2*np.pi*1j*self.carrier_freq*time_array)

        # Compute filter boundaries
        # Lowend is half the baud (i.e. the fundamental of the data)
        # Highend blocks fundamental of data and optionally voice
        # TODO: improve this part
        carrier_refl=min(2*self.carrier_freq,self.fs-2*self.carrier_freq)
        filter_lowend=0.5*self.baud
        filter_highend=carrier_refl-filter_lowend
        if carrier_refl-4000>self.carrier_freq:
            filter_highend=carrier_refl-4000

        # Construct FIR filter, filter demodulated signal
        fir_filt=modulator_utils.lowpass_fir_filter(self.fs, filter_lowend, filter_highend)
        filt_delay=(len(fir_filt)-1)//2
        # First append filt_delay number of zeros to incoming signal
        demod_signal=np.pad(demod_signal,(0,filt_delay))
        filtered_demod_signal=signal.lfilter(fir_filt,1,demod_signal)

        # Extract the original amplitudes via averaging of plateau

        # Round to account for floating point weirdness
        interval_count=int(np.round(
            len(modulated_data)/samples_per_symbol))
        interval_offset=filt_delay
        list_constellation=list()

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
            avg=modulator_utils.average_interval_data(filtered_demod_signal, 
                interval_begin, interval_end)
            list_constellation.append(np.conj(avg))

        # Convert observations and mapping into vq arguments
        # Insert the null symbol 0 to account for beginning and end
        list_constellation=[[np.real(point),np.imag(point)] for point in list_constellation]
        code_book=[self.amplitude*np.exp(1j*self.phase_list[i])
                    for i in range(len(self.phase_list))]
        code_book.insert(0,0+0j)
        code_book=[[np.real(obs),np.imag(obs)] for obs in code_book]

        # Map averages to amplitude points
        vector_cluster=vq(list_constellation,code_book)
        # Subtract data points by 1 and remove 0 padding
        # Neat side effect: -1 is an invalid data point
        datastream=vector_cluster[0]-1
        if (datastream[0]!=-1 or datastream[-1]!=-1
                or any(datastream[1:-1]==-1)):
            warnings.warn("Corrupted datastream detected while demodulating",
                ModulationIntegrityWarning)
        return datastream[1:-1]
