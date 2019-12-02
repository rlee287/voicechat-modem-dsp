import random
import numpy as np

import pytest

from voicechat_modem_dsp.modulators.modulator_utils import *

epsilon=1e-14

def test_property_generate_timearray():
    for _ in range(256):
        n=random.randint(1,50000)
        timearr=generate_timearray(n,n+1)
        assert timearr[0]==0
        assert all(np.abs(np.diff(timearr)-1/n) < epsilon)
        assert np.abs(timearr[-1]-1) < epsilon

def test_unit_average_int():
    dataseq=np.asarray([1,1,4,1])
    assert average_interval_data(dataseq,0,3)==2

    assert average_interval_data(dataseq,0,1)==1
    assert average_interval_data(dataseq,1,2)==2.5
    assert average_interval_data(dataseq,2,3)==2.5

def test_unit_average_interp():
    dataseq=[3,1,0,5]
    assert np.abs(average_interval_data(dataseq,0.5,0.5)-2)<epsilon
    assert np.abs(average_interval_data(dataseq,2.8,2.8)-4)<epsilon

def test_unit_average_float():
    dataseq=np.asarray([2,2,2,3,4])
    assert average_interval_data(dataseq,0.5,1.75)==2

def test_unit_average_invalid():
    dataseq=[4,1,3,6,1,2,10,2,5]
    with pytest.raises(ValueError, match=r".*must be larger than.*"):
        average_interval_data(dataseq,4.9,1.6)
    with pytest.raises(ValueError, match=r"Invalid index.*"):
        average_interval_data(dataseq,-1,28.9)

def test_property_average_constant():
    for _ in range(256):
        n=random.randint(1,5000)
        const_val=random.random()
        list_constant=[const_val]*n
        for _ in range(16):
            lower_bound=random.random()*(n-1)
            upper_bound=random.random()*(n-1)
            if upper_bound<lower_bound:
                temp=lower_bound
                lower_bound=upper_bound
                upper_bound=temp
            average=average_interval_data(list_constant,
                    lower_bound,upper_bound)
            assert np.abs(average-const_val)<epsilon

def test_property_average_triangle():
    for _ in range(256):
        n=random.randint(2,5000)
        range_data=list(range(n))
        for _ in range(16):
            upper_bound=random.randrange(n-1)
            assert average_interval_data(range_data,
                    0,upper_bound)==upper_bound/2
