import random
import warnings
import numpy as np

from voicechat_modem_dsp.encoders.encode_pad import *
from voicechat_modem_dsp.modulators.modulator_ask import ASKModulator
from voicechat_modem_dsp.modulators.modulator_utils import ModulationIntegrityWarning

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

def test_property_ask_integrity():
    amplitude_list=list(np.linspace(0.1,1,16))
    count_run=0
    while count_run<256:
        # Shuffle as opposed to complete random to test all 0x00-0xff
        list_data=list(range(256))
        random.shuffle(list_data)
        bitstream=bytes(list_data)
        datastream=base_16_encode(bitstream)

        sampling_freq=get_rand_float(8000,48000)
        carrier_freq=get_rand_float(256,sampling_freq/3)
        baud_rate=get_rand_float(128,carrier_freq/4)

        with warnings.catch_warnings():
            try:
                modulator=ASKModulator(sampling_freq,
                    carrier_freq,amplitude_list,baud_rate)
            except ModulationIntegrityWarning:
                continue

        modulated_data=modulator.modulate(datastream)
        modulator.demodulate(modulated_data)
        demodulated_bundle=modulator.demodulate(modulated_data)
        recovered_bitstream=base_16_decode(demodulated_bundle)
        count_run+=1

        assert bitstream==recovered_bitstream
