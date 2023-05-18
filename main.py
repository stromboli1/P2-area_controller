# Imports
import socket
import struct
from sqlalchemy.orm import sessionmaker
from utils import engine
from models import HousePool, HDData
from start_protocol import onoff_houses
from threading import Thread
from time import sleep
import atexit

from data_analysis import param_check, send_command
from clk_sync import clk_sync

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
            
            if unix_timestamp > 86460:
                raise Exception('Whole day passed')

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
        off_list = []
        while True:
            sleep(1)
            try:
                command = send_command(off_list)
                if command == None:
                    continue
                if type(command[1]) == int:
                    off_list.append(command[1])
                    off_list.remove(command[0])
                elif command[1] and len(off_list) > 0:
                    off_list.remove(command[0])
                elif not command[1]:
                    off_list.append(command[0])
            except Exception as e:
                print("Crashed")
                print(e)

class SendClkSync(Thread):
    def run(self):
        while True:
            sleep(60)
            clk_sync()


onoff_houses(on_off = True)
atexit.register(onoff_houses)

recv_unpack = RecvUnpack()
recv_unpack.start()

sendcommand = SendCommand()
sendcommand.start()

#send_clk_sync = SendClkSync()
#send_clk_sync.start()
