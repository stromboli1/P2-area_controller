# imports
import socket

def onoff_houses() -> None:

    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    start_sock.sendto(b'\x01', ('255.255.255.255', 6969))
    start_sock.close()
