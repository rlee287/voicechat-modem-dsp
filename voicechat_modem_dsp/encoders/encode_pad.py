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
        elif emit_symbol_counter==1:
            rollover_counter+=(2 if bit else 0)
            rollover_counter+=1
        else: #if emit_symbol_counter==0
            rollover_counter+=(4 if bit else 0)
            rollover_counter+=1
    if emit_symbol_counter!=0:
        return_list.append(rollover_counter)
    return return_list

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
    bytearr_ret=bytearray(base64.b32encode(bitstream))
    # Remove padding because we do not need it for this use case
    bytearr_ret.replace("=","")
    return bytes(bytearr_ret)

def base_64_encode(bitstream):
    bytearr_ret=bytearray(base64.b64encode(bitstream))
    # Remove padding because we do not need it for this use case
    bytearr_ret.replace("=","")
    return bytes(bytearr_ret)

# Bitstream already base 256 so conversion is a no-op
def base_256_encode(bitstream):
    return list(bitstream)

def base_256_decode(datastream):
    # Catch ValueError to provide our own message here
    try:
        return bytes(datastream)
    except ValueError:
        raise ValueError("Illegal symbol detected in datastream")

# Deliberately use NaN here for NumPy propagation later
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