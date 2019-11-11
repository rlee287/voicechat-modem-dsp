import numpy as np
from scipy import signal

"""
Computes a time array given a sampling rate and a sample count
"""
def generate_timearray(fs, sample_count):
    dt=1/fs
    return np.arange(0,dt*sample_count,dt)

"""
Computes the number of samples per symbol given a baud and sampling rate

Note: This rate may not be an integer
"""
def samples_per_symbol(fs, baud):
    return fs/baud

"""
Computes the average of the data over the specified interval with integrals.

The bounds on the given interval need not be integers.
Trapezoidal interpolation is used the average integral formula.

Note: Due to trapezoidal approximation this will not produce the
normal average if the bounds are integers. In addition to the 1/2 for endpoints,
The endpoints are explicitly included here, unlike for normal array slicing.
"""
def average_interval_data(data, begin, end):
    width=end-begin

    # Get bounding indicies
    begin_index=int(np.floor(begin))
    begin_frac=begin-begin_index
    end_index=int(np.ceil(end))-1
    end_frac=1-end+np.ceil(end)

    # Increment begin_index to exclude start element
    # Increment end_index to include second-to-last element but exclude last
    sum_interval=sum(data[begin_index+1:end_index+1])

    # Compute beginning contribution
    begin_val=(1-begin_frac)**2 * data[begin_index] \
            + begin_frac*(1-begin_frac)*data[begin_index+1]
    begin_val*=0.5
    # Compute ending contribution
    end_val=end_frac*(1-end_frac)*data[end_index] \
            + end_frac**2*data[end_index+1]
    end_val*=0.5

    # Add this to the sum and average by dividing out width
    sum_inverval+=(begin_val+end_val)
    return sum_interval/width


"""
Computes a gaussian smoothing filter given sampling rate and sigma time
"""
def compute_gaussian_window(fs, sigma_dt):
    sigma=sigma_dt*fs
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
def lowpass_fir_filter(fs,cutoff_low,cutoff_high,attenuation=80):
    tap_count=fred_harris_fir_tap_count(fs,cutoff_high-cutoff_low,attenuation)
    lowpass_filt=signal.remez(tap_count,
            [0,cutoff_low,cutoff_high,0.5*fs],[1,0],fs=fs)
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
