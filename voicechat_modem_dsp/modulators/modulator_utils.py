import numpy as np
from scipy import signal
from scipy.interpolate import interp1d

"""
Warning to be raised when modulators cannot guarantee data accuracy
"""
class ModulationIntegrityWarning(UserWarning):
    pass

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
        if index_int==len(data)-1:
            return data[index_int]
        else:
            return (1-index_frac)*data[index_int]+index_frac*data[index_int+1]

    # Calculate linear interpolation for endpoints
    # Handle special cases where endpoints are end to avoid indexing errors
    # Do not do this for begin as width==0 would have taken care of that already
    begin_int=int(np.floor(begin))
    begin_frac=begin-np.floor(begin_int)
    begin_lininterp=(1-begin_frac)*data[begin_int]+begin_frac*data[begin_int+1]

    if end==len(data)-1:
        end_lininterp=data[end]
    else:
        end_int=int(np.floor(end))
        end_frac=end-np.floor(end)
        end_lininterp=(1-end_frac)*data[end_int]+end_frac*data[end_int+1]

    # Construct input to numpy.trapz
    x_array=list(range(int(np.ceil(begin)),int(np.floor(end))+1))
    y_array=[data[i] for i in x_array]

    x_array=np.asarray([begin]+x_array+[end])
    y_array=np.asarray([begin_lininterp]+y_array+[end_lininterp])

    return np.trapz(y_array,x_array)/width

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
Uses scipy.signal.firls for Least Squares FIR Filter Design
"""
def lowpass_fir_filter(fs,cutoff_low,cutoff_high,attenuation=80):
    if cutoff_low>=cutoff_high:
        raise ValueError("High cutoff must be larger than low cutoff")
    if cutoff_low>=0.5*fs or cutoff_high>=0.5*fs:
        raise ValueError("Cutoffs must be lower than Nyquist limit")

    tap_count=fred_harris_fir_tap_count(fs,cutoff_high-cutoff_low,attenuation)

    # Remez would sometimes return NaN arrays as filters
    # Least-Squares is not iterative so it may have better stability?
    #lowpass_filt=signal.remez(tap_count,
    #        [0,cutoff_low,cutoff_high,0.5*fs],[1,0],fs=fs)
    lowpass_filt=signal.firls(tap_count,[0,cutoff_low,cutoff_high,0.5*fs],
            [1,1,0,0],fs=fs)
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

def goertzel_iir(freq,fs):
    # See https://www.dsprelated.com/showarticle/796.php for derivation
    if freq>=0.5*fs:
        raise ValueError("Desired peak frequency is too high")
    norm_freq=2*np.pi*freq/fs
    numerator=[1,-np.exp(-1j*norm_freq)]
    denominator=[1,-2*np.cos(norm_freq),1]
    return (numerator,denominator)