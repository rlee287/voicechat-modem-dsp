from .ecc_bitstream_base import BaseBitstreamECC
from ..bitstream import read_bitstream, read_bitstream_iterator, write_bitstream

import math
import numpy as np

class GeneratorMatrixECC(BaseBitstreamECC):
    def __init__(self, generator_matrix):
        self.generator_matrix = generator_matrix.as_type(np.int_)
        generator_matrix_shape = generator_matrix.shape
        # G has more columns than rows, G.T is otherwise
        if generator_matrix_shape[0]>generator_matrix_shape[1]:
            self.generator_matrix=self.generator_matrix.T
    
    @property
    def generator_rows(self):
        # length of linear code (output word size)
        return self.generator_matrix.shape[0]
    @property
    def generator_cols(self):
        # rank of linear code (input word size)
        return self.generator_matrix.shape[1]
    
    def encode(self, raw_bitstream):
        output_arr=bytearray(math.ceil(
            len(raw_bitstream)*self.generator_rows/self.generator_cols))
        output_index=0
        for i in range(0, 8*len(raw_bitstream), self.generator_cols):
            list_bits=list()
            for j in range(self.generator_cols):
                list_bits.append(read_bitstream(raw_bitstream,i))
            input_vector=np.asarray(list_bits,dtype=np.int_)
            codeword=input_vector @ self.generator_matrix
            # assert len(codeword)=self.generator_rows
            for j in range(self.generator_rows):
                write_bitstream(output_arr, output_index, codeword[j])
                output_index+=1
    def decode(self, ecc_bitstream):
        output_arr=bytearray(math.floor(
            len(ecc_bitstream)*self.generator_cols/self.generator_rows))
        output_index=0
        for i in range(0, 8*len(ecc_bitstream), self.generator_rows):
            list_bits=list()
            for j in range(self.generator_cols):
                list_bits.append(read_bitstream(ecc_bitstream,i))
            input_vector=np.asarray(list_bits,dtype=np.int_)
            # Complete this with syndrome decoding
