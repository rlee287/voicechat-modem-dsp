import warnings
import numpy as np

from voicechat_modem_dsp.encoders.encode_pad import *
from voicechat_modem_dsp.modulators import ModulationIntegrityWarning, \
    ASKModulator, FSKModulator, PSKModulator, QAMModulator

import pytest

@pytest.mark.unit
def test_invalid_nyquist():
    with pytest.raises(ValueError, match=r"Carrier frequency is too high.+"):
        bad_modulator=ASKModulator(1000,600,np.linspace(0.2,1,8),20)
    with pytest.raises(ValueError, match=r"Baud is too high.+"):
        bad_modulator=ASKModulator(1000,100,np.linspace(0.2,1,8),80)

    with pytest.raises(ValueError, match=r"Carrier frequency is too high.+"):
        bad_modulator=PSKModulator(1000,600,1,np.linspace(0,np.pi,8),20)
    with pytest.raises(ValueError, match=r"Baud is too high.+"):
        bad_modulator=PSKModulator(1000,100,1,np.linspace(0,np.pi,8),80)

    with pytest.raises(ValueError, match=r"Carrier frequency is too high.+"):
        bad_modulator=QAMModulator(1000,600,np.linspace(0.2,1,8),20)
    with pytest.raises(ValueError, match=r"Baud is too high.+"):
        bad_modulator=QAMModulator(1000,100,np.linspace(0.2,1,8),80)

    with pytest.raises(ValueError, match=r"Baud is too high.+"):
        bad_modulator=FSKModulator(1000,1,np.linspace(200,1000,8),800)
    with pytest.raises(ValueError, match=r"Maximum frequency is too high.+"):
        bad_modulator=FSKModulator(1000,0.9,np.linspace(200,600,16),100)

    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=ASKModulator(900,400,np.linspace(0.2,1,8),100)
        bad_modulator=PSKModulator(900,400,1,np.linspace(0,np.pi,8),100)

@pytest.mark.unit
def test_invalid_modspecific():
    with pytest.raises(ValueError, match=r"Invalid amplitudes.+"):
        bad_modulator=ASKModulator(1000,200,np.linspace(-1,2,16),20)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=ASKModulator(2000,880,np.geomspace(0.01,0.5,4),40)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=ASKModulator(2000,880,np.geomspace(0.2,1,256),40)

    with pytest.raises(ValueError, match=r"Invalid phases.+"):
        bad_modulator=PSKModulator(1000,200,1,np.linspace(-1,10,16),20)
    with pytest.raises(ValueError, match=r"amplitude must be positive.+"):
        bad_modulator=PSKModulator(1000,200,-1,np.linspace(0,3*np.pi/2,16),20)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=PSKModulator(1000,200,1,np.linspace(0,0.1,16),50)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=PSKModulator(2000,880,1,np.linspace(0,3*np.pi/2,16),20)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=PSKModulator(1000,200,0.02,np.linspace(0,0.1,16),50)

    with pytest.raises(ValueError, match=r"of constellation points.+"):
        bad_modulator=QAMModulator(1000,200,[2,4,-2j,1+1j],50)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=QAMModulator(2000,880,np.geomspace(0.2,1,256),40)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=QAMModulator(2000,880,[0.05,1j],80)

    with pytest.raises(ValueError, match=r"Frequencies.+positive.?"):
        bad_modulator=FSKModulator(1000,1,np.linspace(-1,1000,16),500)
    with pytest.raises(ValueError, match=r"amplitude must be positive.+"):
        bad_modulator=FSKModulator(1000,-1,np.linspace(100,200,16),20)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=FSKModulator(1000,0.02,np.linspace(100,200,16),20)
