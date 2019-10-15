def read_bitpos(bitstream,position):
    if position<0 or position>=8*len(bitstream):
        raise ValueError("Position index is out of range")
    byteindex=position//8
    shift_val=7-position%8
    return bool((bitstream[byteindex] & (1<<shift_val)) >> shift_val)

def write_bitpos(bitstream, position, bit):
    # Modifies bitstream in place so raise TypeError if wrong type
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