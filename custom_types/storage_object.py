from ctypes import c_uint8
from dataclasses import dataclass
from typing import Final


@dataclass
class StorageObject:
    value: object
    expires_at: int
    type_encoding: c_uint8 # 4 bits represent the encoding, 4 bits represent the type


OBJ_TYPE_STRING: Final[c_uint8] = 0 << 4
OBJ_ENCODING_RAW: c_uint8 = 0
OBJ_ENCODING_INT: c_uint8 = 1
OBJ_ENCODING_EMBSTR: c_uint8 = 8
