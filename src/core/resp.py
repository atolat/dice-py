# Helper functions for all datatypes
def _read_simple_string(data):
    # Simple string starts with +
    idx = 1
    buff = []
    while idx < len(data) and data[idx] != '\r':
        buff.append(data[idx])
        idx += 1
    return "".join(buff), idx + 2


def _read_error(data):
    return _read_simple_string(data)


def _read_int_64(data):
    # First char for int is :
    idx = 1
    n = 0
    while idx < len(data) and data[idx] != '\r':
        n = n * 10 + int(data[idx])
        idx += 1
    return n, idx + 2


def _read_bulk_string(data):
    # Bulk strings start with a $ followed by length
    length, idx = _read_int_64(data)
    return "".join(data[idx:idx + length]), idx + length + 2


def _read_array(data):
    # Arrays start with *
    length, idx = _read_int_64(data)
    out = [None for _ in range(length)]
    for i in range(length):
        ele, offset = _decode_helper(data[idx:])
        out[i] = ele
        idx += offset
    return out, idx


def _decode_helper(data: str, datatype=None):
    if len(data) == 0:
        return None, 0
    match data[0], datatype:
        case '+', None:
            return _read_simple_string(data)
        case '+', 'simple_string':
            return _read_simple_string(data)
        case '-', None:
            return _read_error(data)
        case '-', 'error':
            return _read_error(data)
        case ':', None:
            return _read_int_64(data)
        case ':', 'int64':
            return _read_int_64(data)
        case '$', None:
            return _read_bulk_string(data)
        case '$', 'bulk_string':
            return _read_bulk_string(data)
        case '*', None:
            return _read_array(data)
        case '*', 'array':
            return _read_array(data)
        case _:
            return None, 0


def resp_decode(data: bytes, datatype=None):
    if len(data) == 0:
        return ""
    data = data.decode('utf-8')
    print('decoded', data)
    value, _ = _decode_helper(data, datatype)
    return value


def resp_encode(data, is_bulk):
    match data:
        case str():
            if not is_bulk:
                return str.encode(f'+{data}\r\n')
            else:
                return str.encode(f'${len(data)}\r\n{data}\r\n')
        case _:
            return str.encode('')


def decode_array_string(data):
    value = resp_decode(data)
    return value
