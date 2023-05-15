# Importing modules
from models import HousePool, HDData
from utils import engine
from control_protocol import ControlPacket

# Importing Libraries
from sqlalchemy.orm import sessionmaker
import socket

# Making session
Session = sessionmaker(bind = engine)
session = Session()

def clk_sync() -> None:
    """Sends clk sync packet to household subcontrollers.

    Args:

    Returns:
        None:
    """

    latest_clk: list[int] = []
    house_ips: list[str] = []
    data_objects = session.query(HDData)

    for house in session.query(HousePool):
        house_data = data_objects.filter(
                HDData.house_id == house.id
                ).order_by(HDData.timestamp.desc()).first()

        if house_data == None:
            continue

        latest_clk.append(house_data.timestamp)
        house_ips.append(house.ip)

    largest_clk: int = max(latest_clk)
    largest_clk += 60
    packet = ControlPacket()
    packet.add_clksync(largest_clk)

    print(f'Setting time to: {largest_clk}')
    for ip in house_ips:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 42069))
        sock.send(packet.get_packet())
        sock.close()
