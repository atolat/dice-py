from socket import socket
from typing import List

from src.core.custom_types.redis_command import RedisCommand
from src.core.resp import resp_encode


def eval_ping(args: List[str], c: socket):
    print(f"I'm in eval ping with args -- {args}")
    if len(args) > 1:
        raise Exception("ERR wrong number of arguments for 'ping' command")
    if len(args) == 0:
        print(f"I'm stuck in eval ping, my args are {args}")
        c.sendall(resp_encode("PONG", False))
    else:
        print(f"I'm stuck in eval ping, my args are {args}")
        c.sendall(resp_encode(args[0], True))


def eval_and_respond(cmd: RedisCommand, c: socket):
    print(f'command received in eval and respond: {cmd.cmd}')
    match cmd.cmd:
        case 'PING':
            return eval_ping(cmd.args, c)
        case _:
            print("I'm not PING")
            return eval_ping(cmd.args, c)
