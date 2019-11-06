from .modulator_base import Modulator

class FSKModulator(Modulator):
    def __init__(self, fs, freq_list, baud):
        if baud>=0.5*max(freq_list):
            raise ValueError("Baud is too high to be modulated "+
                             "using given frequencies")
        if fs<=2*max(freq_list):
            raise ValueError
        self.fs=fs
        self.freq_list=freq_list
        self.baud=baud
    
    def modulate(self, data):
        timesamples_needed=len(data)*self.samples_per_symbol
        time_array=Modulator.generate_time_array(self.fs,timesamples_needed)
        current_sin_timestamp=0
        # Incremental addition is a form of integration
        # Frequency in the end is the derivative of phase
    def demodulate(self, time_array, datastream):
        raise NotImplementedError