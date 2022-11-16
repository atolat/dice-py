from ctypes import c_uint8
from typing import Tuple

from custom_types import OBJ_TYPE_STRING, OBJ_ENCODING_INT, OBJ_ENCODING_EMBSTR, OBJ_ENCODING_RAW


def deduce_type_encoding(val: str) -> Tuple[c_uint8, c_uint8]:
    o_type = OBJ_TYPE_STRING
    try:
        int(val, base=10)
        return o_type, OBJ_ENCODING_INT
    except ValueError:
        print("Not an int")
    if len(val) <= 44:
        return o_type, OBJ_ENCODING_EMBSTR
    return o_type, OBJ_ENCODING_RAW
