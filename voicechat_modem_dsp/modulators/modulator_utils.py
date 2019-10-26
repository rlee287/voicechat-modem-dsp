import numpy as np
from scipy import signal

"""
Computes a gaussian smoothing filter given time dt and sigma
"""
def compute_gaussian_window(dt, sigma_dt):
    sigma=sigma_dt/dt
    sample_count=np.ceil(6*sigma+1)
    if sample_count%2==0:
        sample_count+=1
    return signal.windows.gaussian(sample_count, sigma)


"""
Uses fred harris' rule-of-thumb to estimate a FIR tap count

Formula from https://dsp.stackexchange.com/questions/37646/filter-order-rule-of-thumb
"""
def fred_harris_fir_tap_count(fs, transition_width, db_attenuation):
    #N=[fs/delta(f)]∗[atten(dB)/22]
    filter_tap_count=fs/transition_width
    filter_tap_count*=db_attenuation/22
    filter_tap_count=int(np.ceil(filter_tap_count))
    if filter_tap_count%2==0:
        filter_tap_count+=1
    return filter_tap_count

"""
Computes lowpass FIR filter given cutoffs
Uses the SciPy implementation of the Remez Exchange Algorithm
"""
def lowpass_fir_filter(dt,cutoff_low,cutoff_high,attenuation=80):
    tap_count=fred_harris_fir_tap_count(1/dt,cutoff_high-cutoff_low,attenuation)
    lowpass_filt=signal.remez(tap_count,
            [0,cutoff_low,cutoff_high,0.5/dt],[1,0],fs=1/dt)
    # TODO: remove zeros?
    return lowpass_filt

"""
Helper function that takes symmetric "linear-phase" FIR filter
and makes it truly linear-phase

Based on the technique described in https://www.cypress.com/file/123191/download
"""
def linearize_fir(fir_filter):
    frequencies,response=signal.freqz(fir_filter)
    # TODO fill in the rest of this code if this ends up being actually used
    raise NotImplementedError