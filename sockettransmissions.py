import socket

PORT = 42069

def send_packet(packet: bytes, client_addr: str) -> None:
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((client_addr, PORT))
    soc.send(packet)
    soc.close()
