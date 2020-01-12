from .encode_pad import *

# Convenience mapping to allow for lookup based on len(modulation_list)
encode_function_mappings: Dict[int,Callable[[readable_bytearr], List[int]]]= \
    {2:base_2_encode, 4:base_4_encode,
     8:base_8_encode, 16:base_16_encode,
     32:base_32_encode, 64:base_64_encode,
     256:base_256_encode}
decode_function_mappings: Dict[int,Callable[[List[int]], readable_bytearr]]= \
    {2:base_2_decode, 4:base_4_decode,
     8:base_8_decode, 16:base_16_decode,
     32:base_32_decode, 64:base_64_decode,
     256:base_256_decode}

__all__=["encode_function_mappings","decode_function_mappings"]
