from .modulator_base import BaseModulator

from . import modulator_utils
from .modulator_qam import QAMModulator
from .modulator_utils import ModulationIntegrityWarning

import numpy as np
from scipy import signal
from scipy.cluster.vq import vq

import warnings

class PSKModulator(BaseModulator):
    def __init__(self, fs, carrier, amplitude, phase_list, baud):
        # Checks commented out are already included in QAMModulator

        #if carrier<=0:
        #    raise ValueError("Frequency of carrier must be positive")
        #if baud>=0.5*carrier:
        #    raise ValueError("Baud is too high to be modulated "+
        #                     "using carrier frequency")
        # Nyquist limit
        #if carrier>=0.5*fs:
        #    raise ValueError("Carrier frequency is too high for sampling rate")
        if any((x>=2*np.pi or x<0 for x in phase_list)):
            raise ValueError("Invalid phases given")

        if amplitude>1 or amplitude<=0:
            raise ValueError("Base amplitude must be positive and at most 1")

        self.amplitude=amplitude
        self.fs=fs
        self.phase_list=dict(enumerate(phase_list))
        self.carrier_freq=carrier
        self.baud=baud
#        if carrier>=(1/3)*fs:
#            warnings.warn("Carrier frequency is too high to guarantee "
#                          "proper lowpass reconstruction",
#                          ModulationIntegrityWarning)
        if amplitude<0.1:
            warnings.warn("Amplitude may be too small to allow "
                          "reliable reconstruction",ModulationIntegrityWarning)
        if any(dx<=(0.05*2*np.pi) for dx in np.diff(sorted(phase_list))):
            warnings.warn("Phases may be too close "
                          "to be distinguishable from each other",
                          ModulationIntegrityWarning)
        constellation_points=amplitude*np.exp(1j*np.asarray(phase_list))
        self.qam_modulator=QAMModulator(self.fs,self.carrier_freq,
            constellation_points,self.baud)

    @property
    def _calculate_sigma(self):
        return self.qam_modulator._calculate_sigma()

    def modulate(self, datastream):
        return self.qam_modulator.modulate(datastream)

    def demodulate(self, modulated_data):
        return self.qam_modulator.demodulate(modulated_data)
