# Import Modules
import socket

def broadcast_signal(startstop: bool) -> None:
    """Broadcast the start/stop signal.

    Args:
        startstop (bool): Start or stop signal

    Returns:
        None:
    """
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set socket options
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send Broadcast
    sock.sendto(startstop.to_bytes(1, 'big'), ('255.255.255.255', 6969))
