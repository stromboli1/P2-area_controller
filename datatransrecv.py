# Import modules
import struct
import socket

# Create socket object
PORT = 42070
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.bind(('', PORT))

def receive_data_packet() -> tuple[int, float, float, int, tuple[str, int]]:
    """Receives data packet from Household Sub-controller and unpacks it.

    Args:

    Returns:
        tuple[int, float, float, int, tuple[str, int]]: Unpacked data.
    """
    # Ready to receive data
    packet, addr = soc.recvfrom(256)

    # Unpacks data
    devices = packet[0]
    powerusage = round(struct.unpack('f',packet[1:5])[0], 3)
    temperature = round(struct.unpack('f',packet[5:9])[0], 3)
    clk = int.from_bytes(packet[9:13], 'big')

    # Returns the unpacked data as a tuple
    return devices, powerusage, temperature, clk, addr
