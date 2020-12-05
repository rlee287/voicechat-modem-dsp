import random
import warnings
import numpy as np
from scipy.signal import hilbert

from voicechat_modem_dsp.encoders.encode_pad import *
from voicechat_modem_dsp.modulators import ModulationIntegrityWarning, \
    ASKModulator, FSKModulator, PSKModulator, QAMModulator

import pytest

def get_rand_float(lower, upper):
    return random.random()*(upper-lower)+lower

@pytest.mark.filterwarnings("ignore")
@pytest.mark.unit
def test_unit_ask_integrity_novoice():
    amplitude_list=list(np.linspace(0.1,1,16))
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

@pytest.mark.filterwarnings("ignore")
@pytest.mark.unit
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

@pytest.mark.unit
def test_unit_fsk_integrity_bell_202():
    frequency_list=[1200,2200]
    # Shuffle as opposed to complete random to test all 0x00-0xff
    list_data=list(range(256))
    bitstream=bytes(list_data)
    datastream=base_2_encode(bitstream)

    sampling_freq=48000
    amplitude=0.5
    baud_rate=1200

    modulator=FSKModulator(sampling_freq,amplitude,frequency_list,baud_rate)
    modulated_data=modulator.modulate(datastream)
    demodulated_datastream=modulator.demodulate(modulated_data)
    recovered_bitstream=base_2_decode(demodulated_datastream)

    assert bitstream==recovered_bitstream

@pytest.mark.filterwarnings("ignore")
@pytest.mark.unit
def test_unit_fsk_integrity_high_pitch():
    frequency_list=[8000,10000,12000,14000]
    # Shuffle as opposed to complete random to test all 0x00-0xff
    list_data=list(range(256))
    bitstream=bytes(list_data)
    datastream=base_4_encode(bitstream)

    sampling_freq=48000
    amplitude=0.5
    baud_rate=4000

    modulator=FSKModulator(sampling_freq,amplitude,frequency_list,baud_rate)
    modulated_data=modulator.modulate(datastream)
    demodulated_datastream=modulator.demodulate(modulated_data)
    recovered_bitstream=base_4_decode(demodulated_datastream)

    assert bitstream==recovered_bitstream

@pytest.mark.unit
def test_property_silence_corruption():
    amplitude_list=[0.25,0.5,0.75,1]
    phase_list=2*np.pi*np.asarray([0,0.25,0.5,0.75])
    qam_list=[0.5+0.5j,0.5-0.5j,-0.5-0.5j,-0.5+0.5j]
    freq_list=[50,100,150,200]
    input_sequence=[0,1,3,2,3,1,0,1,2,3]

    ask_mod=ASKModulator(1000,100,amplitude_list,25)
    psk_mod=PSKModulator(1000,100,1,phase_list,25)
    qam_mod=QAMModulator(1000,100,qam_list,25)
    fsk_mod=FSKModulator(1000,1,freq_list,25)

    ask_out=ask_mod.modulate(input_sequence)
    psk_out=psk_mod.modulate(input_sequence)
    qam_out=qam_mod.modulate(input_sequence)
    fsk_out=fsk_mod.modulate(input_sequence)

    ask_out[len(ask_out)//2:]=0
    psk_out[len(psk_out)//2:]=0
    qam_out[len(qam_out)//2:]=0
    fsk_out[len(fsk_out)//2:]=0

    with pytest.warns(ModulationIntegrityWarning):
        ask_recovered_sequence=ask_mod.demodulate(ask_out)
        assert -1 in ask_recovered_sequence
    with pytest.warns(ModulationIntegrityWarning):
        psk_recovered_sequence=psk_mod.demodulate(ask_out)
        assert -1 in psk_recovered_sequence
    with pytest.warns(ModulationIntegrityWarning):
        qam_recovered_sequence=qam_mod.demodulate(ask_out)
        assert -1 in qam_recovered_sequence
    with pytest.warns(ModulationIntegrityWarning):
        fsk_recovered_sequence=fsk_mod.demodulate(ask_out)
        assert -1 in fsk_recovered_sequence

@pytest.mark.property
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
        carrier_freq=get_rand_float(256,sampling_freq/2)
        baud_rate=get_rand_float(128,carrier_freq/4)

        with warnings.catch_warnings():
            warnings.simplefilter("error",category=ModulationIntegrityWarning)
            try:
                modulator=ASKModulator(sampling_freq,
                    carrier_freq,amplitude_list,baud_rate)
            except ModulationIntegrityWarning:
                continue

        modulated_data=modulator.modulate(datastream)

        # Imaginary part of analytic signal is phase shifted 90 degrees
        # Randomize the phase of the modulated signal
        # Demodulation should not care about signal phase
        modulated_data_analytic=hilbert(modulated_data)
        modulated_data_analytic*=np.exp(2j*np.pi*random.random())
        modulated_data_phaseshifted=np.real(modulated_data_analytic)

        demodulated_bundle=modulator.demodulate(modulated_data_phaseshifted)
        recovered_bitstream=base_16_decode(demodulated_bundle)
        count_run+=1

        assert bitstream==recovered_bitstream

@pytest.mark.property
def test_property_psk_integrity():
    phase_list=list(np.linspace(0,2*np.pi,16,endpoint=False))
    count_run=0
    while count_run<256:
        # Shuffle as opposed to complete random to test all 0x00-0xff
        list_data=list(range(256))
        random.shuffle(list_data)
        bitstream=bytes(list_data)
        datastream=base_16_encode(bitstream)

        sampling_freq=get_rand_float(8000,48000)
        carrier_freq=get_rand_float(256,sampling_freq/2)
        baud_rate=get_rand_float(128,carrier_freq/4)
        amplitude=get_rand_float(0.1,1)

        with warnings.catch_warnings():
            warnings.simplefilter("error",category=ModulationIntegrityWarning)
            try:
                modulator=PSKModulator(sampling_freq,
                    carrier_freq,amplitude,phase_list,baud_rate)
            except ModulationIntegrityWarning:
                continue

        modulated_data=modulator.modulate(datastream)
        demodulated_bundle=modulator.demodulate(modulated_data)

        recovered_bitstream=base_16_decode(demodulated_bundle)
        count_run+=1

        assert bitstream==recovered_bitstream

@pytest.mark.property
def test_property_qam_integrity():
    constellation_list=[-1-1j,-1-1/3j,-1+1/3j,-1+1j,
                        -1/3-1j,-1/3-1/3j,-1/3+1/3j,-1/3+1j,
                        1/3-1j,1/3-1/3j,1/3+1/3j,1/3+1j,
                        1-1j,1-1/3j,1+1/3j,1+1j]
    constellation_list=np.asarray(constellation_list)
    constellation_list/=np.max(np.abs(constellation_list))
    count_run=0
    while count_run<256:
        # Shuffle as opposed to complete random to test all 0x00-0xff
        list_data=list(range(256))
        random.shuffle(list_data)
        bitstream=bytes(list_data)
        datastream=base_16_encode(bitstream)

        sampling_freq=get_rand_float(8000,48000)
        carrier_freq=get_rand_float(256,sampling_freq/2)
        baud_rate=get_rand_float(128,carrier_freq/4)
        amplitude=get_rand_float(0.1,1)

        with warnings.catch_warnings():
            warnings.simplefilter("error",category=ModulationIntegrityWarning)
            try:
                modulator=QAMModulator(sampling_freq,
                    carrier_freq,constellation_list,baud_rate)
            except ModulationIntegrityWarning:
                continue

        modulated_data=modulator.modulate(datastream)
        demodulated_bundle=modulator.demodulate(modulated_data)

        recovered_bitstream=base_16_decode(demodulated_bundle)
        count_run+=1

        assert bitstream==recovered_bitstream

@pytest.mark.property
def test_property_fsk_integrity():
    frequency_list=list(np.linspace(512,2048,16))
    count_run=0
    while count_run<256:
        # Shuffle as opposed to complete random to test all 0x00-0xff
        list_data=list(range(256))
        random.shuffle(list_data)
        bitstream=bytes(list_data)
        datastream=base_16_encode(bitstream)

        sampling_freq=get_rand_float(8000,48000)
        amplitude=get_rand_float(0.1,1)
        baud_rate=get_rand_float(64,256)

        with warnings.catch_warnings():
            warnings.simplefilter("error",category=ModulationIntegrityWarning)
            try:
                modulator=FSKModulator(sampling_freq,
                    amplitude,frequency_list,baud_rate)
            except ModulationIntegrityWarning:
                continue

        modulated_data=modulator.modulate(datastream)
        demodulated_bundle=modulator.demodulate(modulated_data)
        recovered_bitstream=base_16_decode(demodulated_bundle)
        count_run+=1

        assert bitstream==recovered_bitstream
