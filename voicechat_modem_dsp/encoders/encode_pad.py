from .bitstream import read_bitstream_iterator

import base64

# In custom encoders, return bytes as output type
# for compatibility with base64 module functions
def base_2_encode(bitstream):
    return_list=list()
    for bit in read_bitstream_iterator(bitstream):
        return_list.append(1 if bit else 0)
    return bytes("".join((str(x) for x in return_list)))

def base_4_encode(bitstream):
    return_list=list()
    rollover_counter=0
    emit_symbol=False
    for bit in read_bitstream_iterator(bitstream):
        if emit_symbol:
            rollover_counter+=(1 if bit else 0)
            return_list.append(rollover_counter)
            rollover_counter=0
        else:
            rollover_counter+=(2 if bit else 0)
        emit_symbol=not emit_symbol
    return bytes("".join((str(x) for x in return_list)))

def base_8_encode(bitstream):
    return_list=list()
    rollover_counter=0
    emit_symbol_counter=0
    for bit in read_bitstream_iterator(bitstream):
        # Could also bit-shift and increment
        # Writing cases out explicitly is more readable however
        if emit_symbol_counter==2:
            rollover_counter+=(1 if bit else 0)
            return_list.append(rollover_counter)
            rollover_counter=0
        elif emit_symbol_counter==1:
            rollover_counter+=(2 if bit else 0)
            rollover_counter+=1
        else: #if emit_symbol_counter==0
            rollover_counter+=(4 if bit else 0)
            rollover_counter+=1
    if emit_symbol_counter!=0:
        return_list.append(rollover_counter)
    return bytes("".join((str(x) for x in return_list)))

def base_16_encode(bitstream):
    return base64.b16encode(bitstream)

def base_32_encode(bitstream):
    bytearr_ret=bytearray(base64.b32encode(bitstream))
    # Remove padding because we do not need it for this use case
    bytearr_ret.replace("=","")
    return bytes(bytearr_ret)

def base_64_encode(bitstream):
    bytearr_ret=bytearray(base64.b64encode(bitstream))
    # Remove padding because we do not need it for this use case
    bytearr_ret.replace("=","")
    return bytes(bytearr_ret)

# Bitstream already base 256 so this is a no-op
def base_256_encode(bitstream):
    return bitstream

def make_pad_array(datastream, pad_len):
    list_ret=[float("nan")]*pad_len
    list_ret+=list(datastream)
    list_ret+=[float("nan")]+pad_len
    return list_ret

def unpad_array(datastream):
    list_ret=datastream.copy()
    while list_ret[0]==float("nan"):
        del list_ret[0]
    while list_ret[-1]==float("nan"):
        del list_ret[-1]
    return list_ret