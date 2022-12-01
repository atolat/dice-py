from ctypes import c_uint8, c_uint32
from dataclasses import dataclass, field
from typing import Final


@dataclass(eq=True)
class StorageObject:
    value: object = field(compare=False)
    expires_at: int
    # Store the last accessed at timestamp -- redis allocates 24 bits for this
    last_accessed_at: int
    type_encoding: c_uint8  # 4 bits represent the encoding, 4 bits represent the type

    def __hash__(self):
        return id(self)


OBJ_TYPE_STRING: Final[c_uint8] = 0 << 4
OBJ_ENCODING_RAW: c_uint8 = 0
OBJ_ENCODING_INT: c_uint8 = 1
OBJ_ENCODING_EMBSTR: c_uint8 = 8
