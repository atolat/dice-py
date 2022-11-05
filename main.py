# Import the library
import argparse
import os.path
from configparser import ConfigParser
import socket

from src.server import sync_tcp_server
from src.server.sync_tcp_server import run_sync_tcp_server_v2


def main():
    # Set defaults for host and port
    host = socket.gethostbyname(socket.gethostname())
    port = 56789
    config_dir = 'config.conf'
    config = ConfigParser()
    if os.path.isfile(config_dir):
        config.read(config_dir)
        config_dict = dict(config.items('default'))
        host = config_dict.get('host', host)
        port = config_dict.get('port', port)
    else:
        print('Config does not exist, using defaults')
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=host)
    parser.add_argument('--port', type=int, default=port)
    args = parser.parse_args()
    run_sync_tcp_server_v2(args.host, args.port)


if __name__ == '__main__':
    main()
