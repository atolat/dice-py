import selectors
import socket
import types

from src.core.eval import EvalException
from src.server.sync_tcp_server import _read_command, _respond_v2, _respond_error


def accept_wrapper(sel, sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(sel, key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            cmd = _read_command(recv_data)
            response = _respond_v2(cmd)
            data.outb += response
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def run_async_tcp_server(host, port):
    print(f'Starting an asynchronous TCP server on HOST: {host}, PORT: {port}')
    max_clients = 2000

    # Create the listener socket
    listener_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_sock.bind((host, port))
    listener_sock.listen()
    print(f"Listening on {(host, port)}")

    # Set the socket to operate in non-blocking mode
    listener_sock.setblocking(False)

    # AsyncIO starts here...
    # For python implementation, we will use the selectors module, it abstracts the underlying async mechanism -
    # epoll, kqueue

    # Create the selector
    sel = selectors.DefaultSelector()

    # Register the listener
    sel.register(listener_sock, selectors.EVENT_READ, data=None)

    # Event Loop
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(sel, key.fileobj)
                else:
                    try:
                        service_connection(sel, key, mask)
                    except EvalException as ee:
                        key.fileobj.send(_respond_error(str(ee)))
                        print(f"Exception while reading or decoding data, more info - {ee}")
                    except Exception as e:
                        key.fileobj.send(_respond_error(str(e)))
                        print(f"Exception while reading or decoding data, more info - {e}")
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()
