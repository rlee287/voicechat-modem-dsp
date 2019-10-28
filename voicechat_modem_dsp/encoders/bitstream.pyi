# Type stub for encoders.bitstream (Python 3)

from typing import Union, Iterator

readable_bytearr=Union[bytes, bytearray]
writeable_bytearr=Union[bytearray]

def read_bitstream(bitstream: readable_bytearr, position: int) -> bool: ...
def read_bitstream_iterator(bitstream: readable_bytearr) -> Iterator[bool]: ...
def write_bitstream(bitstream: writeable_bytearr,
                    position: int, bit: bool) -> None: ...
