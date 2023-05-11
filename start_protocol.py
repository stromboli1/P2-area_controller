# imports
import socket

def onoff_houses(on_off = False) -> None:

    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    start_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    if on_off:
        start_sock.sendto(b'\x01', ('10.10.0.255', 6969))
        start_sock.close()
    elif not on_off:
        start_sock.sendto(b'\x00', ('<broadcast>', 6969))
        start_sock.close()
