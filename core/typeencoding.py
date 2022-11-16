from ctypes import c_uint8


class TypeEncodingException(Exception):
    pass


def get_type(te: c_uint8) -> c_uint8:
    return 0b11110000 & te


def get_encoding(te: c_uint8) -> c_uint8:
    return 0b00001111 & te


def assert_type(te: c_uint8, t: c_uint8):
    if get_type(te) != t:
        raise TypeEncodingException('Operation not permitted on this type')
    return None


def assert_encoding(te: c_uint8, e: c_uint8):
    if get_encoding(te) != e:
        raise TypeEncodingException('Operation not permitted on this encoding')
    return None
