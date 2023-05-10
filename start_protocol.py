# imports
import socket
from models import HousePool
from sqlalchemy.orm import sessionmaker
from utils import engine

# create session
Session = sessionmaker(bind = engine)
session = Session()

def onoff_houses() -> None:

    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for house in session.query(HousePool):
        start_sock.sendto(b'\x01', (house.ip, 6969))
    start_sock.close()
