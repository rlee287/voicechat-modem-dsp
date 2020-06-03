from .ecc_bitstream_base import BaseBitstreamECC

class NoECC(BaseBitstreamECC):
    """
    Passthrough object that does not perform any ECC
    """
    def encode(self, raw_bitstream):
        return bytes(raw_bitstream)
    def decode(self, ecc_bitstream):
        return bytes(ecc_bitstream)