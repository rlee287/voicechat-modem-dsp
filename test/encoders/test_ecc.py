import random

import pytest

from voicechat_modem_dsp.encoders.bitstream import *
from voicechat_modem_dsp.encoders.ecc import NoECC, Hamming_7_4_ECC

@pytest.mark.property
def test_property_passthrough_ecc_is_nop():
    dummy_ecc=NoECC()
    for _ in range(4):
        n=random.randint(1,256)
        data_test=bytearray((random.getrandbits(8) for _ in range(n)))
        encoded_data_test=dummy_ecc.encode(data_test)
        recovered_perfect=dummy_ecc.decode(encoded_data_test)
        assert data_test==recovered_perfect
        assert data_test==encoded_data_test

@pytest.mark.property
def test_property_corrupt_hamming_nonmangle():
    hamming_ecc=Hamming_7_4_ECC()
    for _ in range(64):
        n=random.randint(1,256)
        data_test=bytearray((random.getrandbits(8) for _ in range(n)))
        hamming_data_test=hamming_ecc.encode(data_test)
        recovered_perfect=hamming_ecc.decode(hamming_data_test)
        assert data_test==recovered_perfect

@pytest.mark.property
def test_property_corrupt_hamming_recoverable_err():
    hamming_ecc=Hamming_7_4_ECC()
    for _ in range(64):
        n=random.randint(1,256)
        data_test=bytearray((random.getrandbits(8) for _ in range(n)))
        hamming_data_test=bytearray(hamming_ecc.encode(data_test))
        for index in range(0,8*n,7):
            index_offset=index+random.randrange(7)
        write_bitstream(hamming_data_test,index_offset,
                        not read_bitstream(hamming_data_test,index_offset))
        recovered_corrected=hamming_ecc.decode(hamming_data_test)
        assert data_test==recovered_corrected
