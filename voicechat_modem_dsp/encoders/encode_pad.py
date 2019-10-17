from .bitstream import read_bitstream_iterator

# Return string for compatibility with base64 module functions
def base_2_encode(bitstream):
    return_list=list()
    for bit in read_bitstream_iterator(bitstream):
        return_list.append(1 if bit else 0)
    return "".join((str(x) for x in return_list))   

# Return string for compatibility with base64 module functions
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
    return "".join((str(x) for x in return_list)) 

# Return string for compatibility with base64 module functions
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
    return "".join((str(x) for x in return_list)) 