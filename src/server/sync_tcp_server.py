import socket
from src.core.custom_types.redis_command import *
from src.core.eval import eval_and_respond
from src.core.resp import resp_decode


def _respond_error(error, c):
    c.sendall(str.encode(f'-{error}\r\n'))


class SyncTCPServer:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    @staticmethod
    def _read_command(data, c: socket) -> (RedisCommand, str):
        # data = c.recv(1024)
        print(f'Received: {data}')
        decoded_data = resp_decode(data)
        cmd = "COMMAND"
        args = ["ARGS"]
        if decoded_data:
            cmd, args = decoded_data[0], decoded_data[1:]
        print(f'COMMAND--{cmd}, ARGS -- {args}')
        return RedisCommand(cmd=cmd.upper(), args=args)

    @staticmethod
    def _respond(cmd: RedisCommand, c: socket):
        try:
            eval_and_respond(cmd, c)
        except Exception as e:
            _respond_error(str(e), c)

    def run_sync_tcp_server(self):
        print(f'Starting a synchronous TCP server on HOST: {self.host}, PORT: {self.port}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    # try:
                    #     data = self._read_command(conn)
                    #     if not data:
                    #         break
                    #     self._respond(data, conn)
                    # except Exception as e:
                    #     print(f"Something went wrong -- {e}")
                    #     # raise e
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    print(f"AHHHA--{data.decode('utf-8')}")
                    # if not data or data.decode('utf-8') == '':
                    #     break
                    cmd = self._read_command(data, conn)
                    self._respond(cmd, conn)
