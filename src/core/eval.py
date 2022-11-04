from socket import socket
from typing import List

from src.core.custom_types.redis_command import RedisCommand
from src.core.resp import resp_encode


class EvalException(Exception):
    pass


def eval_ping_v2(args: List[str]):
    if len(args) > 1:
        print(f'Encoding BAD args for ping -- {args}')
        raise EvalException("ERR wrong number of arguments for 'ping' command")
    if len(args) == 0:
        encoded_data = resp_encode("PONG", False)
        return encoded_data
    else:
        print(f'Encoding args for ping -- {args}')
        encoded_data = resp_encode(args[0], True)
        return encoded_data


def eval_and_respond_v2(cmd: RedisCommand):
    match cmd.cmd:
        case 'PING':
            return eval_ping_v2(cmd.args)
        case _:
            return eval_ping_v2(cmd.args)
