from abc import ABC, abstractmethod

from ..bitstream import readable_bytearr, writeable_bytearr

# Functions should accept either bytes or bytearrays
# Manipulate bytearrays during construction but return bytes
# Once encoded, data should be immutable
class BaseBitstreamECC(ABC):
    """
    Base ECC class defining interface for different ECC methods
    """
    @abstractmethod
    def encode(self, raw_bitstream: readable_bytearr) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def decode(self, ecc_bitstream: readable_bytearr) -> bytes:
        raise NotImplementedError