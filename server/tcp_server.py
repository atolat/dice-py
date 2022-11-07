from abc import ABC, abstractmethod

from core.custom_types.redis_command import RedisCommand
from core.eval import eval_and_respond
from core.resp import resp_decode


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
    def respond(cmd: RedisCommand) -> str:
        try:
            to_send = eval_and_respond(cmd)
            return to_send
        except Exception as e:
            raise e

    @staticmethod
    def respond_error(error: str) -> bytes:
        return str.encode(f'-{error}\r\n')