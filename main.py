# Import the library
import argparse
import socket

from config.config import *
from server.async_tcp_server import run_server


def main():
    # Set defaults for host and port
    default_host = host or socket.gethostbyname(socket.gethostname())
    default_port = port or 56789
    default_mode = mode or 'async'
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=default_host)
    parser.add_argument('--port', type=int, default=default_port)
    parser.add_argument('--mode', type=str, default=default_mode)
    args = parser.parse_args()
    if args.mode == 'sync':
        run_server(args.host, args.port)
    else:
        run_server(args.host, args.port)


if __name__ == '__main__':
    main()
