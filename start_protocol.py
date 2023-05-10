# imports
import socket

def start_houses() -> None:

    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_sock.sendto(b'\x01', 6969)
    start_sock.close()

def stop_houses() -> None:

    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_sock.sendto(b'\x00', 6969)
    start_sock.close()
