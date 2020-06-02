import math

from .base_ecc import BaseECC
from ..bitstream import read_bitstream, write_bitstream
from ..bitstream import readable_bytearr

class Hamming_7_4_ECC(BaseECC):
    """
    Performs ECC using a Hamming 7,4 code
    """
    def encode(self, bitstream):
        output_arr=bytearray(math.ceil(len(bitstream)*7/4))
        output_index=0
        for i in range(0,8*len(bitstream),4):
            byteindex=i//8
            bitpos=7-i%8
            bit3=bool(bitstream[byteindex] & 1<<bitpos)
            bit5=bool(bitstream[byteindex] & 1<<(bitpos-1))
            bit6=bool(bitstream[byteindex] & 1<<(bitpos-2))
            bit7=bool(bitstream[byteindex] & 1<<(bitpos-3))
            # Use bitwise xor operator here since type is bool already
            bit1=bit3 ^ bit5 ^ bit7
            bit2=bit3 ^ bit6 ^ bit7
            bit4=bit5 ^ bit6 ^ bit7
            
            # Write computed data
            write_bitstream(output_arr,output_index,bit1)
            write_bitstream(output_arr,output_index+1,bit2)
            write_bitstream(output_arr,output_index+2,bit3)
            write_bitstream(output_arr,output_index+3,bit4)
            write_bitstream(output_arr,output_index+4,bit5)
            write_bitstream(output_arr,output_index+5,bit6)
            write_bitstream(output_arr,output_index+6,bit7)
            output_index+=7
        return bytes(output_arr)

    def decode(self, bitstream):
        output_arr=bytearray(math.floor(len(bitstream)*4/7))
        output_index=0
        for i in range(0,8*len(bitstream),7):
            try:
                bit3=read_bitstream(bitstream,i+2)
                bit5=read_bitstream(bitstream,i+4)
                bit6=read_bitstream(bitstream,i+5)
                bit7=read_bitstream(bitstream,i+6)
                bit1=read_bitstream(bitstream,i)
                bit2=read_bitstream(bitstream,i+1)
                bit4=read_bitstream(bitstream,i+3)
            except ValueError:
                # Less than 7 elements left at the end, ignore padding
                break

            # Use bitwise operator here since type is bool already
            bit1_correct=bit3 ^ bit5 ^ bit7
            bit2_correct=bit3 ^ bit6 ^ bit7
            bit4_correct=bit5 ^ bit6 ^ bit7
            # Use != here even though xor because semantically this is a comparison
            bit1_error=(bit1 != bit1_correct)
            bit2_error=(bit2 != bit2_correct)
            bit4_error=(bit4 != bit4_correct)
            # Booleans are integers 0 or 1 so below multiplication works
            error_location=bit1_error+2*bit2_error+4*bit4_error
            # Correct data bits if wrong but don't bother fixing wrong parity bits
            if error_location==3:
                bit3=not bit3
            elif error_location==5:
                bit5=not bit5
            elif error_location==6:
                bit6=not bit6
            elif error_location==7:
                bit7=not bit7

            write_bitstream(output_arr,output_index,bit3)
            write_bitstream(output_arr,output_index+1,bit5)
            write_bitstream(output_arr,output_index+2,bit6)
            write_bitstream(output_arr,output_index+3,bit7)
            output_index+=4
        return bytes(output_arr)
