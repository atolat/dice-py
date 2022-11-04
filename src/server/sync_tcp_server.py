import socket
import sys

from src.core.custom_types.redis_command import *
from src.core.eval import eval_and_respond_v2, EvalException
from src.core.resp import resp_decode


def _respond_error(error):
    return str.encode(f'-{error}\r\n')


def _read_command(data) -> (RedisCommand, str):
    decoded_data = resp_decode(data)
    cmd = "COMMAND"
    args = ""
    if decoded_data:
        cmd, args = decoded_data[0], decoded_data[1:]
    return RedisCommand(cmd=cmd.upper(), args=args)


def _respond_v2(cmd: RedisCommand):
    try:
        to_send = eval_and_respond_v2(cmd)
        return to_send
    except Exception as e:
        raise e


def run_sync_tcp_server_v2(host, port):
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
                        cmd = _read_command(data)
                        response = _respond_v2(cmd)
                        c.send(response)
                    except EvalException as ee:
                        c.send(_respond_error(str(ee)))
                        print(f"Exception while reading or decoding data, more info - {ee}")
                    except Exception as e:
                        c.send(_respond_error(str(e)))
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
