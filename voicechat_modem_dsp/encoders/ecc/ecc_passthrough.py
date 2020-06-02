from .base_ecc import BaseECC

class NoECC(BaseECC):
    """
    Passthrough object that does not perform any ECC
    """
    def encode(self, raw_bitstream):
        return bytes(raw_bitstream)
    def decode(self, ecc_bitstream):
        return bytes(ecc_bitstream)