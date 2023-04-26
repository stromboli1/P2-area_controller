#module import
import socket
import struct
from sqlalchemy.orm import sessionmaker
from utils import engine
from models import HousePool, HDData

#variables
PORT = 42070
ADDR = ""

#setup database session
Session = sessionmaker(bind = engine)
session = Session()

#setup socket udp server
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.bind((ADDR, PORT))

#listen for incoming messages
while True:
    byte_message = soc.recvfrom(1024)
    data, house_addr = byte_message

    device_state: int = data[0]
    power_usage: float = struct.unpack(">f", data[1:5])[0]
    temperature: float = struct.unpack(">f", data[5:9])[0]
    unix_timestamp: int = int.from_bytes(data[9:13], 'big')

    house_id = session.query(HousePool).filter(
            HousePool.ip == house_addr[0]
            ).first().id

    entry = HDData(device_state = device_state,
                   power_usage = power_usage,
                   temperature = temperature,
                   timestamp = unix_timestamp,
                   house_id = house_id)

    session.add(entry)
    session.commit()
