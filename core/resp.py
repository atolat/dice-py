# Helper functions for all datatypes
def read_simple_string(data):
    # Simple string starts with +
    idx = 1
    buff = []
    while idx < len(data) and data[idx] != '\r':
        buff.append(data[idx])
        idx += 1
    return "".join(buff), idx + 2


def read_error(data):
    return read_simple_string(data)


def read_int_64(data):
    # First char for int is :
    idx = 1
    n = 0
    while idx < len(data) and data[idx] != '\r':
        n = n * 10 + int(data[idx])
        idx += 1
    return n, idx + 2


def read_bulk_string(data):
    # Bulk strings start with a $ followed by length
    length, idx = read_int_64(data)
    return "".join(data[idx:idx + length]), idx + 2


def read_array(data):
    # Arrays start with *
    length, idx = read_int_64(data)
    out = [None for _ in range(length)]
    for i in range(length):
        ele, offset = decode_helper(data[idx:])
        out[i] = ele
        idx += offset
    return out, idx


def decode_helper(data):
    if len(data) == 0:
        return None, 0
    match data[0]:
        case '+':
            return read_simple_string(data)
        case '-':
            return read_error(data)
        case ':':
            return read_int_64(data)
        case '$':
            return read_bulk_string(data)
        case '*':
            return read_array(data)
        case _:
            return None, 0


def decode(data):
    if len(data) == 0:
        return None
    value, _ = decode_helper(data)
    return value


# TODO : Move tests to unittest
print(decode("+OK\r\n"))
print(decode("-Error message\r\n"))
print(decode(":0\r\n"))
print(decode(":1000\r\n"))
print(decode("$5\r\nhello\r\n"))
print(decode("$0\r\n\r\n"))
print(decode("*0\r\n"))
print(decode("*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n"))
print(decode("*3\r\n:1\r\n:2\r\n:3\r\n"))
print(decode("*5\r\n:1\r\n:2\r\n:3\r\n:4\r\n$5\r\nhello\r\n"))
print(decode("*2\r\n*3\r\n:1\r\n:2\r\n:3\r\n*2\r\n+Hello\r\n-World\r\n"))
