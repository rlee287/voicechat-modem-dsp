import random
import numpy as np

from voicechat_modem_dsp.encoders.encode_pad import *
from voicechat_modem_dsp.modulators.modulator_ask import ASKModulator

import pytest

def get_rand_float(lower, upper):
    return random.random()*(upper-lower)+lower

def test_unit_ask_integrity_novoice():
    amplitude_list=list(np.geomspace(0.1,1,16))
    list_data=list(range(256))
    bitstream=bytes(list_data)
    datastream=base_16_encode(bitstream)

    sampling_freq=48000
    carrier_freq=1000
    baud_rate=250

    modulator=ASKModulator(sampling_freq,carrier_freq,amplitude_list,baud_rate)
    modulated_data=modulator.modulate(datastream)
    demodulated_datastream=modulator.demodulate(modulated_data)
    recovered_bitstream=base_16_decode(demodulated_datastream)

    assert bitstream==recovered_bitstream

def test_unit_ask_integrity_voice():
    amplitude_list=list(np.geomspace(0.1,1,16))
    # Shuffle as opposed to complete random to test all 0x00-0xff
    list_data=list(range(256))
    bitstream=bytes(list_data)
    datastream=base_16_encode(bitstream)

    sampling_freq=48000
    carrier_freq=8000
    baud_rate=1000

    modulator=ASKModulator(sampling_freq,carrier_freq,amplitude_list,baud_rate)
    modulated_data=modulator.modulate(datastream)
    demodulated_datastream=modulator.demodulate(modulated_data)
    recovered_bitstream=base_16_decode(demodulated_datastream)

    assert bitstream==recovered_bitstream

@pytest.mark.skip(reason="Need to manually check behavior with pathological inputs")
def test_property_ask_integrity():
    amplitude_list=list(np.geomspace(0.1,1,16))
    for _ in range(4):
        # Shuffle as opposed to complete random to test all 0x00-0xff
        list_data=list(range(256))
        random.shuffle(list_data)
        bitstream=bytes(list_data)
        datastream=base_16_encode(bitstream)

        sampling_freq=get_rand_float(8000,48000)
        carrier_freq=get_rand_float(100,0.5*sampling_freq)
        baud_rate=get_rand_float(50,0.5*carrier_freq)

        modulator=ASKModulator(sampling_freq,carrier_freq,amplitude_list,baud_rate)
        modulated_data=modulator.modulate(datastream)
        demodulated_datastream=modulator.demodulate(modulated_data)
        recovered_bitstream=base_16_decode(demodulated_datastream)

        assert bitstream==recovered_bitstream
