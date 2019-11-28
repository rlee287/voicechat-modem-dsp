import numpy as np
from scipy import signal
from scipy.interpolate import interp1d

"""
Computes a time array given a sampling rate and a sample count
"""
def generate_timearray(fs, sample_count):
    dt=1/fs
    return np.linspace(0,dt*sample_count,sample_count,endpoint=False)

"""
Computes the number of samples per symbol given a baud and sampling rate

Note: Neither quantity has to be an integer
"""
def samples_per_symbol(fs, baud):
    return fs/baud

"""
Maps a sequence (assumed to be sampled at baud rate) to a timesequence
"""
def previous_resample_interpolate(timeseq, baud, data):
    interp_func=interp1d(range(len(data)),data,
        kind="previous",copy=False,bounds_error=False,fill_value=0.0)
    return interp_func(timeseq*baud)

"""
Computes the average of the data over the specified interval with integrals.

The bounds on the given interval need not be integers.
Linear interpolation is used for noninteger bounds.

See "Trapezoidal Averaging.ipynb" for derivations of these formulas.

Note: Due to trapezoidal approximation this will not produce the
normal average if the bounds are integers.
Both endpoints are explicitly included, unlike normal array slicing.
In addition, the values at the extremities receive half the weight
as the rest of the data, following the trapezoidal integration formula.
"""
def average_interval_data(data, begin, end):
    if end<begin:
        raise ValueError("End must be larger than begin")
    if begin<0 or end>(len(data)-1):
        raise ValueError("Invalid index range specified")
    width=end-begin
    # Handle special case of width=0
    if width==0:
        index_int=int(np.floor(begin))
        index_frac=begin-np.floor(begin)
        return (1-index_frac)*data[index_int]+index_frac*data[index_int+1]

    # Get bounding indicies
    begin_index=int(np.floor(begin))
    begin_frac=begin-begin_index
    end_index=int(np.ceil(end))-1
    end_frac=1-(np.ceil(end)-end)

    if end_index-begin_index>0:
        if end_index-begin_index==1:
            # Case 2: two trapezoids with no whole trapezoids in between
            # Compute the portion of the trapzeoid normally folded into sum
            # Lump sum does not work because the widths are smaller
            sum_interval=data[end_index]*(1-begin_frac+end_frac)
            sum_interval*=0.5
        else:
            # Case 3: general trapezoidal integration
            # Increment begin_index to exclude start element
            # Increment end_index to include second-to-last element
            # but exclude last
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
        sum_interval+=(begin_val+end_val)
    else:
        # Case 1: A single trapezoid
        # begin_index and end_index equal here, but separate for readability
        sum_interval=(end_frac-begin_frac)* \
            ((1-begin_frac)*data[begin_index]+begin_frac*data[begin_index+1]+ \
            (1-end_frac)*data[end_index]+end_frac*data[end_index+1])
        sum_interval*=0.5
    return sum_interval/width


"""
Computes a gaussian smoothing filter given sampling rate and sigma time
"""
def gaussian_window(fs, sigma_dt):
    sigma=sigma_dt*fs
    sample_count=np.ceil(6*sigma+1)
    if sample_count%2==0:
        sample_count+=1
    raw_window=signal.windows.gaussian(sample_count, sigma)
    raw_window_sum=np.sum(raw_window)
    return raw_window/raw_window_sum


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
and makes it truly linear-phase by removing zeros

Based on the technique described in https://www.cypress.com/file/123191/download
"""
def linearize_fir(fir_filter):
    frequencies,response=signal.freqz(fir_filter)
    # TODO fill in the rest of this code if this ends up being actually used
    raise NotImplementedError
