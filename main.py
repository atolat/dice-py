# Import the library
import argparse
from server import sync_tcp_server
import socket
# Create the parser
# parser = argparse.ArgumentParser()
# Add an argument
# parser.add_argument('--name', type=str, required=True)
# Parse the argument
# args = parser.parse_args()
# Print "Hello" + the user input argument
# print(sync_tcp_server.test())

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=HOST)
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()
    sync_server = sync_tcp_server.SyncTCPServer(host=args.host, port=args.port)
    sync_server.run_sync_tcp_server()

if __name__ == '__main__':
    main()
    