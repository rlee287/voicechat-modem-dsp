import random
import numpy as np

from voicechat_modem_dsp.modulators.modulator_utils import *

epsilon=1e-14

def test_property_generate_timearray():
    for _ in range(256):
        n=random.randint(1,50000)
        timearr=generate_timearray(n,n+1)
        assert timearr[0]==0
        assert all(np.abs(np.diff(timearr)-1/n) < epsilon)
        assert np.abs(timearr[-1]-1) < epsilon

def test_unit_average():
    dataseq=np.asarray([1,1,4,1])
    assert average_interval_data(dataseq,0,3)==2

    assert average_interval_data(dataseq,0,1)==1
    assert average_interval_data(dataseq,1,2)==2.5
    assert average_interval_data(dataseq,2,3)==2.5

def test_property_average_uniform():
    pass