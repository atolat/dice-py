import socket
import sys

from core.eval import EvalException
from server.tcp_server import TCPServer


class SyncTCPServer(TCPServer):
    @staticmethod
    def run_server(host: str, port: str):
        print(f'Starting a synchronous TCP server on HOST: {host}, PORT: {port}')
        con_clients = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(5)
        try:
            while True:
                try:
                    c, address = sock.accept()
                    print("Connected from", address)
                    con_clients += 1
                    while True:
                        try:
                            data = c.recv(1024)
                            if not data:
                                break
                            # Try to decode the data to a redis command
                            cmd = TCPServer.read_command(data)
                            response = TCPServer.respond(cmd)
                            c.send(response)
                        except EvalException as ee:
                            c.send(TCPServer.respond_error(str(ee)))
                            print(f"Exception while reading or decoding data, more info - {ee}")
                        except Exception as e:
                            c.send(TCPServer.respond_error(str(e)))
                            print(f"Exception while reading or decoding data, more info - {e}")
                    c.close()
                    con_clients -= 1
                    print("Disconnected from", address)
                except KeyboardInterrupt as ke:
                    print("Received a keyboard interrupt, exiting gracefully")
                    con_clients -= 1
                    sock.close()
                    sys.exit(0)
        finally:
            sock.close()
