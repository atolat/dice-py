# Import the library
import argparse
import os.path
from configparser import ConfigParser
import socket

from server.async_tcp_server import run_server
from server.sync_tcp_server import SyncTCPServer


def main():
    # Set defaults for host and port
    host = socket.gethostbyname(socket.gethostname())
    port = 56789
    default_mode = 'async'
    config_dir = 'config.conf'
    config = ConfigParser()
    if os.path.isfile(config_dir):
        config.read(config_dir)
        config_dict = dict(config.items('default'))
        host = config_dict.get('host', host)
        port = config_dict.get('port', port)
        mode = config_dict.get('mode', default_mode)
    else:
        print('Config does not exist, using defaults')
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=host)
    parser.add_argument('--port', type=int, default=port)
    parser.add_argument('--mode', type=str, default=mode)
    args = parser.parse_args()
    if args.mode == 'sync':
        SyncTCPServer.run_server(args.host, args.port)
    else:
        run_server(args.host, args.port)


if __name__ == '__main__':
    main()
