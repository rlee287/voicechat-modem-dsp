"""Utility functions to read and write bitstreams (bytes or bytearray)"""
from typing import Union, Iterator

readable_bytearr=Union[bytes, bytearray]
writeable_bytearr=Union[bytearray]

# Bitstream functions are MSB first

def read_bitstream(bitstream: readable_bytearr, position: int) -> bool:
    """Return the bit at the given location in the bitstream."""
    if position<0 or position>=8*len(bitstream):
        raise ValueError("Position index is out of range")
    byteindex=position//8
    shift_val=7-position%8
    return bool((bitstream[byteindex] & (1<<shift_val)) >> shift_val)

def read_bitstream_iterator(bitstream: readable_bytearr) -> Iterator[bool]:
    """Create a bitwise interator over the given bitstream."""
    for byte in bitstream:
        for shift_val in range(7,-1,-1):
            yield bool((byte & (1<<shift_val)) >> shift_val)

def write_bitstream(bitstream: writeable_bytearr,
        position: int, bit: bool) -> None:
    """
    Write the bit into the given location in the bitstream.

    This modifies the bitstream in place, so it must be mutable.
    """
    # Raise TypeError if the bitstream is not mutable
    if isinstance(bitstream, bytes):
        raise TypeError("Bitstream should be mutable")
    if position<0 or position>=8*len(bitstream):
        raise ValueError("Position index is out of range")
    byteindex=position//8
    lshift_val=7-position%8
    shifted_bit=1<<lshift_val
    if bit:
        bitstream[byteindex] |= shifted_bit
    else:
        bitstream[byteindex] &= ~shifted_bit
