import warnings
import numpy as np

from voicechat_modem_dsp.encoders.encode_pad import *
from voicechat_modem_dsp.modulators.modulator_ask import ASKModulator
from voicechat_modem_dsp.modulators.modulator_utils import ModulationIntegrityWarning

import pytest

@pytest.mark.unit
def test_invalid_nyquist():
    with pytest.raises(ValueError, match=r"Carrier frequency is too high.+"):
        bad_modulator=ASKModulator(1000,600,np.linspace(0.2,1,8),20)
    with pytest.raises(ValueError, match=r"Baud is too high.+"):
        bad_modulator=ASKModulator(1000,100,np.linspace(0.2,1,8),80)

    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=ASKModulator(900,400,np.linspace(0.2,1,8),100)

@pytest.mark.unit
def test_invalid_modspecific():
    with pytest.raises(ValueError, match=r"Invalid amplitudes.+"):
        bad_modulator=ASKModulator(1000,200,np.linspace(-1,2,16),20)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=ASKModulator(2000,880,np.geomspace(0.01,0.5,4),40)
    with pytest.warns(ModulationIntegrityWarning):
        bad_modulator=ASKModulator(2000,880,np.geomspace(0.2,1,256),40)
