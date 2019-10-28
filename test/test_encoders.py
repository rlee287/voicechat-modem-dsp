import random

import pytest

from voicechat_modem_dsp.encoders.encode_pad import *

def test_unit_bad_datastream_len():
    datastream_singular=[0]
    with pytest.raises(ValueError,match=r".*length"):
        base_2_decode(datastream_singular)
    with pytest.raises(ValueError,match=r".*length"):
        base_4_decode(datastream_singular)
    with pytest.raises(ValueError,match=r".*length"):
        base_8_decode(datastream_singular)
    with pytest.raises(ValueError,match=r".*length"):
        base_16_decode(datastream_singular)
    with pytest.raises(ValueError,match=r".*length"):
        base_32_decode(datastream_singular)
    with pytest.raises(ValueError,match=r".*length"):
        base_64_decode(datastream_singular)
    # Base256 cannot have bad length

def test_unit_bad_datastream():
    datastream_bad_align=[0,1,2,3,-4,5,6,100]
    with pytest.raises(ValueError,match=r"Illegal symbol.*"):
        base_2_decode(datastream_bad_align)
    with pytest.raises(ValueError,match=r"Illegal symbol.*"):
        base_4_decode(datastream_bad_align)
    with pytest.raises(ValueError,match=r"Illegal symbol.*"):
        base_8_decode(datastream_bad_align)
    with pytest.raises(ValueError,match=r"Illegal symbol.*"):
        base_16_decode(datastream_bad_align)
    with pytest.raises(ValueError,match=r"Illegal symbol.*"):
        base_32_decode(datastream_bad_align)
    with pytest.raises(ValueError,match=r"Illegal symbol.*"):
        base_64_decode(datastream_bad_align)
    with pytest.raises(ValueError,match=r"Illegal symbol.*"):
        base_256_decode(datastream_bad_align)

    datastream_malform_base_8=[7,7,7]
    with pytest.raises(ValueError):
        base_8_decode(datastream_malform_base_8)

def test_unit_base_2():
    bitstream=b"\x0f"
    bitstream_list=[0,0,0,0,1,1,1,1]
    encode_list=base_2_encode(bitstream)
    assert encode_list==bitstream_list
    bitstream_list.reverse()
    decode_reverse=base_2_decode(bitstream_list)
    assert decode_reverse==b"\xf0"

def test_property_base_2_turnaround():
    for _ in range(64):
        n=random.randint(1,256)
        data_bitstream=bytearray((random.getrandbits(8) for _ in range(n)))
        data_datastream=base_2_encode(data_bitstream)
        data_bitstream_recover=base_2_decode(data_datastream)
        assert bytes(data_bitstream)==data_bitstream_recover

def test_unit_base_4():
    bitstream=b"\x0f\x81"
    bitstream_list=[0,0,3,3,2,0,0,1]
    encode_list=base_4_encode(bitstream)
    assert encode_list==bitstream_list
    bitstream_list.reverse()
    decode_reverse=base_4_decode(bitstream_list)
    assert decode_reverse==b"\x42\xf0"

def test_property_base_4_turnaround():
    for _ in range(64):
        n=random.randint(1,256)
        data_bitstream=bytearray((random.getrandbits(8) for _ in range(n)))
        data_datastream=base_4_encode(data_bitstream)
        data_bitstream_recover=base_4_decode(data_datastream)
        assert bytes(data_bitstream)==data_bitstream_recover

def test_property_base_8_turnaround():
    for _ in range(64):
        n=random.randint(1,256)
        data_bitstream=bytearray((random.getrandbits(8) for _ in range(n)))
        data_datastream=base_8_encode(data_bitstream)
        data_bitstream_recover=base_8_decode(data_datastream)
        assert bytes(data_bitstream)==data_bitstream_recover

def test_unit_base_16():
    bitstream=b"\x01\x23\x45\x67\x89\xab\xcd\xef"
    bitstream_list=list(range(16))
    encode_list=base_16_encode(bitstream)
    assert encode_list==bitstream_list
    bitstream_list.reverse()
    decode_reverse=base_16_decode(bitstream_list)
    assert decode_reverse==b"\xfe\xdc\xba\x98\x76\x54\x32\x10"

def test_property_base_16_turnaround():
    for _ in range(64):
        n=random.randint(1,256)
        data_bitstream=bytearray((random.getrandbits(8) for _ in range(n)))
        data_datastream=base_16_encode(data_bitstream)
        data_bitstream_recover=base_16_decode(data_datastream)
        assert bytes(data_bitstream)==data_bitstream_recover

def test_property_base_32_turnaround():
    for _ in range(64):
        n=random.randint(1,256)
        data_bitstream=bytearray((random.getrandbits(8) for _ in range(n)))
        data_datastream=base_32_encode(data_bitstream)
        data_bitstream_recover=base_32_decode(data_datastream)
        assert bytes(data_bitstream)==data_bitstream_recover

def test_property_base_64_turnaround():
    for _ in range(64):
        n=random.randint(1,256)
        data_bitstream=bytearray((random.getrandbits(8) for _ in range(n)))
        data_datastream=base_64_encode(data_bitstream)
        data_bitstream_recover=base_64_decode(data_datastream)
        assert bytes(data_bitstream)==data_bitstream_recover

def test_unit_base_256():
    bitstream=b"\x01\x23\x45\x67\x89\xab\xcd\xef"
    bitstream_list=[0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef]
    encode_list=base_256_encode(bitstream)
    assert encode_list==bitstream_list
    bitstream_list.reverse()
    decode_reverse=base_256_decode(bitstream_list)
    assert decode_reverse==b"\xef\xcd\xab\x89\x67\x45\x23\x01"

def test_property_base_256_turnaround():
    for _ in range(64):
        n=random.randint(1,256)
        data_bitstream=bytearray((random.getrandbits(8) for _ in range(n)))
        data_datastream=base_256_encode(data_bitstream)
        data_bitstream_recover=base_256_decode(data_datastream)
        assert bytes(data_bitstream)==data_bitstream_recover
