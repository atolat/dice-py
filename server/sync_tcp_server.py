import socket


class SyncTCPServer:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    @staticmethod
    def __read_command(c: socket):
        data = c.recv(1024)
        print(f'Received: {data}')
        return data

    @staticmethod
    def __respond(cmd: str, c: socket):
        c.sendall(cmd)

    def run_sync_tcp_server(self):
        print(f'Starting a synchronous TCP server on HOST: {self.host}, PORT: {self.port}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    try:
                        data = self.__read_command(conn)
                        if not data:
                            break
                        self.__respond(data, conn)
                    except Exception as e:
                        print(f"Something went wrong -- {e}")
                        raise e
