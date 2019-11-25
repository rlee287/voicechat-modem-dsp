from .bitstream import read_bitstream_iterator, write_bitstream

import base64

# These return a list of numbers corresponding to symbols
def base_2_encode(bitstream):
    return_list=list()
    for bit in read_bitstream_iterator(bitstream):
        return_list.append(1 if bit else 0)
    return return_list

def base_2_decode(datastream):
    base_2_mapping={0:False, 1:True}
    if len(datastream)%8 != 0:
        raise ValueError("Inappropriate datastream length")
    return_bytearray=bytearray(len(datastream)//8)
    for index,bit in enumerate(datastream):
        try:
            write_bitstream(return_bytearray,index,base_2_mapping[bit])
        except KeyError:
            raise ValueError("Illegal symbol detected in datastream")
    return bytes(return_bytearray)

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
    return return_list

def base_4_decode(datastream):
    base_4_mapping={0:(False,False),
                    1:(False,True),
                    2:(True,False),
                    3:(True,True)}
    if len(datastream)%4 != 0:
        raise ValueError("Inappropriate datastream length")
    return_bytearray=bytearray(len(datastream)//4)
    for index,symbol in enumerate(datastream):
        try:
            symbol_entry=base_4_mapping[symbol]
            write_bitstream(return_bytearray,2*index,symbol_entry[0])
            write_bitstream(return_bytearray,2*index+1,symbol_entry[1])
        except KeyError:
            raise ValueError("Illegal symbol detected in datastream")
    return bytes(return_bytearray)

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
            emit_symbol_counter=0
        elif emit_symbol_counter==1:
            rollover_counter+=(2 if bit else 0)
            emit_symbol_counter+=1
        else: #if emit_symbol_counter==0
            rollover_counter+=(4 if bit else 0)
            emit_symbol_counter+=1
    if emit_symbol_counter!=0:
        return_list.append(rollover_counter)
    return return_list

def base_8_decode(datastream):
    base_8_mapping={0:(False,False,False),
                    1:(False,False,True),
                    2:(False,True,False),
                    3:(False,True,True),
                    4:(True,False,False),
                    5:(True,False,True),
                    6:(True,True,False),
                    7:(True,True,True)}
    if len(datastream)%8 not in [0,3,6]:
        raise ValueError("Inappropriate datastream length")
    has_extension=(len(datastream)%8!=0)
    byte_len=3*len(datastream)//8
    if has_extension:
        byte_len+=1
    return_bytearray=bytearray(byte_len)
    for index,symbol in enumerate(datastream):
        try:
            symbol_entry=base_8_mapping[symbol]
            write_bitstream(return_bytearray,3*index,symbol_entry[0])
            write_bitstream(return_bytearray,3*index+1,symbol_entry[1])
            write_bitstream(return_bytearray,3*index+2,symbol_entry[2])
        except KeyError:
            raise ValueError("Illegal symbol detected in datastream")
    if has_extension:
        if return_bytearray[-1]!=0:
            raise ValueError("Malformed datastream: end padding is not 0")
        del return_bytearray[-1]
    return bytes(return_bytearray)

def base_16_encode(bitstream):
    return [int(chr(c), 16) for c in base64.b16encode(bitstream)]

def base_16_decode(datastream):
    if len(datastream)%2!=0:
        raise ValueError("Inappropriate datastream length")
    for c in datastream:
        # Should only require a single hex digit
        if c<0 or hex(c)[-2]!="x":
            raise ValueError("Illegal symbol detected in datastream")
    return base64.b16decode(bytearray("".join([hex(c)[-1] for c in datastream]),
                            "ascii"),casefold=True)

def base_32_encode(bitstream):
    base_32_mapping = {char:int_val for int_val,char in 
        enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")}
    base_32_encodestr=str(base64.b32encode(bitstream),"ascii")
    # Remove padding because we do not need it for this use case
    base_32_encodestr=base_32_encodestr.replace("=","")
    # b32encode works properly -> KeyError impossible
    return [base_32_mapping[char] for char in base_32_encodestr]

def base_32_decode(datastream):
    # Convert to dict to avoid negative index wrapping
    base_32_mapping=dict(enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"))
    try:
        base_32_str="".join([base_32_mapping[c] for c in datastream])
    except KeyError:
        raise ValueError("Illegal symbol detected in datastream")
    add_pad_len=(8-(len(datastream)%8))%8
    base_32_str+="="*add_pad_len
    # TODO specify proper mathematical condition
    try:
        return base64.b32decode(base_32_str)
    except ValueError:
        raise ValueError("Inappropriate datastream length")

def base_64_encode(bitstream):
    base_64_mapping = {char:int_val for int_val,char in
        enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz0123456789+/")}
    base_64_encodestr=str(base64.b64encode(bitstream),"ascii")
    # Remove padding because we do not need it for this use case
    base_64_encodestr=base_64_encodestr.replace("=","")
    # b32encode works properly -> KeyError impossible
    return [base_64_mapping[char] for char in base_64_encodestr]

def base_64_decode(datastream):
    # Convert to dict to avoid negative index wrapping
    base_64_mapping=dict(enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz0123456789+/"))
    try:
        base_64_str="".join([base_64_mapping[c] for c in datastream])
    except KeyError:
        raise ValueError("Illegal symbol detected in datastream")
    if len(datastream)%4==1:
        raise ValueError("Inappropriate datastream length")
    add_pad_len=(4-(len(datastream)%4))%4
    base_64_str+="="*add_pad_len
    return base64.b64decode(base_64_str)

# Bitstream already base 256 so conversion is a no-op
def base_256_encode(bitstream):
    return list(bitstream)

def base_256_decode(datastream):
    # Catch ValueError to provide our own message here
    try:
        return bytes(datastream)
    except ValueError:
        raise ValueError("Illegal symbol detected in datastream")

# Convenience mapping to allow for lookup based on len(modulation_list)
encode_function_mappings = {2:base_2_encode, 4:base_4_encode,
                            8:base_8_encode, 16:base_16_encode,
                            32:base_32_encode, 64:base_64_encode,
                            256:base_256_encode}

decode_function_mappings = {2:base_2_decode, 4:base_4_decode,
                            8:base_8_decode, 16:base_16_decode,
                            32:base_32_decode, 64:base_64_decode,
                            256:base_256_decode}
