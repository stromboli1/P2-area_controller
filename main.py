# Imports
import socket
import struct
from sqlalchemy.orm import sessionmaker
from utils import engine
from models import HousePool, HDData
from threading import Thread
from time import sleep

from data_analysis import send_command

class RecvUnpack(Thread):
    def run(self):
        #variables
        PORT = 42070
        ADDR = ""

        #setup database session
        Session = sessionmaker(bind = engine)
        session = Session()

        #setup socket udp server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ADDR, PORT))

        #listen for incoming messages
        while True:
            byte_message = sock.recvfrom(1024)
            data, house_addr = byte_message

            #unpack message
            device_state: int = data[0]
            power_usage: float = struct.unpack(">f", data[1:5])[0]
            temperature: float = struct.unpack(">f", data[5:9])[0]
            unix_timestamp: int = int.from_bytes(data[9:13], 'big')

            print(f"Received from {house_addr}: {device_state} {power_usage} {temperature} {unix_timestamp}")

            #find correct house in database
            house_id = session.query(HousePool).filter(
                    HousePool.ip == house_addr[0]
                    ).first().id

            #create data entry
            entry = HDData(device_state = device_state,
                        power_usage = power_usage,
                        temperature = temperature,
                        timestamp = unix_timestamp,
                        house_id = house_id)

            #commit data
            session.add(entry)
            session.commit()

class SendCommand(Thread):
    def run(self):
        while True:
            send_command()
            sleep(1)

recv_unpack = RecvUnpack()
recv_unpack.start()

sendcommand = SendCommand()
sendcommand.start()