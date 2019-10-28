from .modulator_base import Modulator

class FSKModulator(Modulator):
    def __init__(self, dt, freq_map, baud):
        if baud>=0.5*max(freq_map.values):
            raise ValueError("Baud is too high to be modulated "+
                             "using given frequencies")
        self.dt=dt
        self.freq_list=freq_list
        self.baud=baud
    
    def modulate(self, data):
        timesamples_needed=len(data)*self.samples_per_symbol
        time_array=Modulator.generate_time_array(self.dt,timesamples_needed)
        current_sin_timestamp=0
        # Incremental addition is a form of integration
        # Frequency in the end is the derivative of phase
    def demodulate(self, time_array, datastream):
        raise NotImplementedError