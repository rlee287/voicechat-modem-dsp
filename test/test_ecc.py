import random

from voicechat_modem_dsp.encoders.ecc.hamming_7_4 import *

def test_property_corrupt_hamming_nonmangle():
    for _ in range(256):
        n=random.randint(1,256)
        data_test=bytearray(random.getrandbits(8) for _ in range(n))
        hamming_data_test=bytearray(hamming_encode_7_4(data_test))
        recovered_perfect=hamming_decode_7_4(hamming_data_test)
        assert data_test==recovered_perfect

def test_property_corrupt_hamming_recoverable_err():
    for _ in range(256):
        n=random.randint(1,256)
        data_test=bytearray(random.getrandbits(8) for _ in range(n))
        hamming_data_test=bytearray(hamming_encode_7_4(data_test))
        for index in range(0,8*n,7):
            index_offset=index+random.randrange(7)
        write_bitstream(hamming_data_test,index_offset,
                        not read_bitstream(hamming_data_test,index_offset))
        recovered_corrected=hamming_decode_7_4(hamming_data_test)
        assert data_test==recovered_corrected