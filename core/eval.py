"""
Logic to parse arguments and evaluate redis commands
"""

import datetime as dt
from typing import List

from core import key_space, resp_encode, deduce_type_encoding, assert_type, assert_encoding, TypeEncodingException, \
    write_aof
from custom_types import RedisCommand, OBJ_TYPE_STRING, OBJ_ENCODING_INT
from storage import put, get, delete, new_storage_object, has_expired, get_expiry, set_expiry, evict_all_keys_LRU


class EvalException(Exception):
    pass


def eval_ping(args: List[str]):
    if len(args) > 1:
        raise EvalException("ERR wrong number of arguments for 'ping' command")
    if len(args) == 0:
        encoded_data = resp_encode("PONG", False)
        return encoded_data
    else:
        encoded_data = resp_encode(args[0], True)
        return encoded_data


def eval_set(args):
    if len(args) <= 1:
        raise EvalException("ERR wrong number of arguments for 'set' command")
    key, val = args[0], args[1]
    o_type, o_encoding = deduce_type_encoding(val)
    expiry_duration_ms, expiry_duration_sec = -1, -1
    i = 2
    while i < len(args):
        if args[i] in ('EX', 'ex'):
            i += 1
            if i == len(args):
                raise EvalException("ERR syntax error")
            try:
                expiry_duration_sec = int(args[3])
            except ValueError:
                raise EvalException("ERR value is not an integer or out of range")
            expiry_duration_ms = expiry_duration_sec * 1000
            break
        else:
            raise EvalException("ERR syntax error")

    put(key, new_storage_object(value=val, duration_ms=expiry_duration_ms, o_type=o_type, o_encoding=o_encoding))
    return str.encode('+OK\r\n')


def eval_get(args):
    if len(args) != 1:
        raise EvalException("ERR wrong number of arguments for 'set' command")
    key = args[0]
    val = get(key)
    if val is None:
        return str.encode('$-1\r\n')

    if has_expired(val):
        return str.encode('$-1\r\n')

    return resp_encode(val.value, is_bulk=True)


def eval_ttl(args):
    if len(args) != 1:
        raise EvalException("ERR wrong number of arguments for 'ttl' command")
    key = args[0]
    val = get(key)
    if val is None:
        return str.encode(':-2\r\n')
    exp = get_expiry(val)
    if exp is None:
        return str.encode(':-1\r\n')
    # duration_ms = val.expires_at - int(dt.datetime.now().timestamp() * 1000)
    if exp < int(dt.datetime.now().timestamp() * 1000):
        return str.encode(':-2\r\n')
    duration_ms = exp - int(dt.datetime.now().timestamp() * 1000)
    return resp_encode(int(duration_ms / 1000))


def eval_delete(args):
    num_delete = 0
    for key in args:
        if delete(key):
            num_delete += 1
    return resp_encode(num_delete)


def eval_incr(args):
    if len(args) != 1:
        raise EvalException("ERR wrong number of arguments for 'incr' command")
    key = args[0]
    obj = get(key)
    if obj is None:
        obj = new_storage_object("0", -1, OBJ_TYPE_STRING, OBJ_ENCODING_INT)
        put(key, obj)
    try:
        assert_type(obj.type_encoding, OBJ_TYPE_STRING)
        assert_encoding(obj.type_encoding, OBJ_ENCODING_INT)
    except TypeEncodingException as tte:
        raise EvalException(str(tte))
    i = int(obj.value, base=10)
    i += 1
    obj.value = str(i)
    return resp_encode(i, True)


def eval_expire(args):
    if len(args) <= 1:
        raise EvalException("ERR wrong number of arguments for 'expire' command")
    key = args[0]
    try:
        expiry_duration_sec = int(args[1])
    except ValueError:
        raise EvalException("(error) ERR value is not an integer or out of range")
    expiry_duration_ms = expiry_duration_sec * 1000

    val = get(key)
    if val is None:
        return str.encode(':0\r\n')
    set_expiry(val, expiry_duration_ms)
    # val.expires_at = int(dt.datetime.now().timestamp() * 1000) + expiry_duration_ms
    return str.encode(':1\r\n')


def eval_bgrewriteaof(args):
    write_aof()
    return str.encode('+OK\r\n')


def eval_info(args):
    buff = ''
    buff += '# Keyspace\r\n'
    for i in range(len(key_space)):
        if 'keys' in key_space[i]:
            buff += f'db{i}:keys={str(key_space[i]["keys"])},expire=0,avg_ttl=0\r\n'
    return resp_encode(buff, True)


def eval_client(args):
    pass


def eval_latency(args):
    pass


def eval_LRU(args):
    evict_all_keys_LRU()
    return str.encode('+OK\r\n')


def eval_and_respond_pipe(cmds: List[RedisCommand]) -> str:
    """
    Command parser - matches commands and passes args to command handler
    :param cmds: Incoming redis command
    :return: Processed response -- RESP encoded byte string
    """
    buffer = b''
    for cmd in cmds:
        match cmd.cmd:
            case 'PING':
                buffer += eval_ping(cmd.args)
            case 'SET':
                buffer += eval_set(cmd.args)
            case 'GET':
                buffer += eval_get(cmd.args)
            case 'TTL':
                buffer += eval_ttl(cmd.args)
            case 'DEL':
                buffer += eval_delete(cmd.args)
            case 'EXPIRE':
                buffer += eval_expire(cmd.args)
            case 'INCR':
                buffer += eval_incr(cmd.args)
            case 'BGREWRITEAOF':
                buffer += eval_bgrewriteaof(cmd.args)
            case 'INFO':
                buffer += eval_info(cmd.args)
            case 'CLIENT':
                buffer += eval_client(cmd.args)
            case 'LATENCY':
                buffer += eval_latency(cmd.args)
            case 'LRU':
                buffer += eval_LRU(cmd.args)
            case _:
                buffer += eval_ping(cmd.args)
    return buffer
