import random

import pytest

from voicechat_modem_dsp.encoders.bitstream import *

@pytest.mark.unit
def test_unit_bitstream_read():
    bitstream=b"\x55\x55"
    for i in range(8*len(bitstream)):
        assert read_bitstream(bitstream,i)==bool(i%2)

@pytest.mark.unit
def test_unit_bitstream_read_iterator():
    bitstream=b"\x00\xff\x55"
    list_bits=list(read_bitstream_iterator(bitstream))
    assert list_bits==[False,False,False,False,
                       False,False,False,False,
                       True,True,True,True,
                       True,True,True,True,
                       False,True,False,True,
                       False,True,False,True]

@pytest.mark.unit
def test_unit_bitstream_write():
    bitstream=bytearray(b"\x00\x00")
    for i in range(8*len(bitstream)):
        write_bitstream(bitstream,i,True)
    for element in bitstream:
        assert element==255

@pytest.mark.unit
def test_unit_bitstream_range():
    with pytest.raises(ValueError):
        read_bitstream(b"",1)
    with pytest.raises(ValueError):
        read_bitstream(b"anything",-1)
    with pytest.raises(ValueError):
        write_bitstream(bytearray(b""),1,True)
    with pytest.raises(ValueError):
        write_bitstream(bytearray(b"anything"),-1,True)

@pytest.mark.unit
def test_unit_write_bitstream_type():
    with pytest.raises(TypeError):
        write_bitstream(b"Not mutable",0,True)
