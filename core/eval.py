import time
from typing import List
import datetime as dt
from core.custom_types.redis_command import RedisCommand
from core.resp import resp_encode
from core.storage.storage import put, get, delete


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
        raise EvalException("(error) ERR wrong number of arguments for 'set' command")
    key, val = args[0], args[1]
    expiry_duration_ms, expiry_duration_sec = -1, -1
    i = 2
    while i < len(args):
        if args[i] in ('EX', 'ex'):
            i += 1
            if i == len(args):
                raise EvalException("(error) ERR syntax error")
            try:
                expiry_duration_sec = int(args[3])
            except ValueError:
                raise EvalException("(error) ERR value is not an integer or out of range")
            expiry_duration_ms = expiry_duration_sec * 1000
            break
        else:
            raise EvalException("(error) ERR syntax error")

    put(key, val, expiry_duration_ms)
    print("I got here!")
    return str.encode('+OK\r\n')


def eval_get(args):
    if len(args) != 1:
        raise EvalException("(error) ERR wrong number of arguments for 'set' command")
    key = args[0]
    val = get(key)
    if val is None:
        return str.encode('$-1\r\n')

    if val.expires_at != -1 and val.expires_at <= int(dt.datetime.now().timestamp() * 1000):
        return str.encode('$-1\r\n')

    return resp_encode(val.value, is_bulk=True)


def eval_ttl(args):
    if len(args) != 1:
        raise EvalException("(error) ERR wrong number of arguments for 'ttl' command")
    key = args[0]
    val = get(key)
    if val is None:
        return str.encode(':-2\r\n')
    if val.expires_at == -1:
        return str.encode(':-1\r\n')
    duration_ms = val.expires_at - int(dt.datetime.now().timestamp() * 1000)
    if duration_ms < 0:
        return str.encode(':-2\r\n')
    return resp_encode(int(duration_ms / 1000))


def eval_delete(args):
    num_delete = 0
    for key in args:
        if delete(key):
            num_delete += 1
    return resp_encode(num_delete)


def eval_expire(args):
    if len(args) <= 1:
        raise EvalException("(error) ERR wrong number of arguments for 'ttl' command")
    key = args[0]
    try:
        expiry_duration_sec = int(args[1])
    except ValueError:
        raise EvalException("(error) ERR value is not an integer or out of range")
    expiry_duration_ms = expiry_duration_sec * 1000

    val = get(key)
    if val is None:
        return str.encode(':0\r\n')

    val.expires_at = int(dt.datetime.now().timestamp() * 1000) + expiry_duration_ms
    return str.encode(':1\r\n')


def eval_and_respond(cmd: RedisCommand):
    match cmd.cmd:
        case 'PING':
            return eval_ping(cmd.args)
        case 'SET':
            return eval_set(cmd.args)
        case 'GET':
            return eval_get(cmd.args)
        case 'TTL':
            return eval_ttl(cmd.args)
        case 'DEL':
            return eval_delete(cmd.args)
        case 'EXPIRE':
            return eval_expire(cmd.args)
        case _:
            return eval_ping(cmd.args)


def eval_and_respond_pipe(cmds: List[RedisCommand]):
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
            case _:
                buffer += eval_ping(cmd.args)
    return buffer
