#module import
import socket
import models
from sqlalchemy.orm import sessionmaker

#variables
PORT = 42070
ADDR = "0.0.0.0"

#setup database session
Session = sessionmaker()
session = Session()

#setup socket udp server
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.bind((ADDR, PORT))

#listen for incoming messages
while True:
    byte_message = soc.recvfrom(1024)

    data = byte_message[0]
    house_ip = byte_message[1]


