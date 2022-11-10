from abc import ABC, abstractmethod
from typing import List, Any

from core.custom_types.redis_command import RedisCommand
from core.eval import eval_and_respond, eval_and_respond_pipe
from core.resp import resp_decode, resp_decode_pipe


class TCPServer(ABC):
    @staticmethod
    @abstractmethod
    def run_server(host: str, port: str):
        pass

    @staticmethod
    def read_command(data: str) -> RedisCommand:
        decoded_data = resp_decode(data)
        cmd = "COMMAND"
        args = ""
        if decoded_data:
            cmd, args = decoded_data[0], decoded_data[1:]
        return RedisCommand(cmd=cmd.upper(), args=args)

    @staticmethod
    def read_commands(data: str) -> List[RedisCommand]:
        decoded_data = resp_decode_pipe(data)
        cmds: list[RedisCommand] = []
        for val in decoded_data:
            tokens = [str(v) for v in val]
            print(f"Tokens -- {tokens}")
            cmds.append(RedisCommand(cmd=tokens[0].upper(), args=tokens[1:]))
        return cmds

    @staticmethod
    def respond(cmd: RedisCommand) -> str:
        try:
            to_send = eval_and_respond(cmd)
            return to_send
        except Exception as e:
            raise e

    @staticmethod
    def respond_pipe(cmds: List[RedisCommand]) -> str:
        try:
            to_send = eval_and_respond_pipe(cmds)
            print(f"Sending: {to_send}")
            return to_send
        except Exception as e:
            raise e

    @staticmethod
    def respond_error(error: str) -> bytes:
        return str.encode(f'-{error}\r\n')