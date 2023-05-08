# imports
import json
import socket
from sqlalchemy.orm import sessionmaker
from models import HousePool, HDData, ActionPool
from utils import engine
from control_protocol import ControlPacket
from time import time

# global variables
action_flag = None

# read config
with open('anal_param.json', 'r') as fd:
    params: dict = json.load(fd)

# create session for database
Session = sessionmaker(bind = engine)
session = Session()

def get_data_from_house(house_id: int) -> tuple[int, float, float, int]:
    """function for getting data from house.

    Args:
        house_id (int): house_id

    Returns:
        tuple[int, float, float, int]:
    """
    data_object = session.query(HDData).filter(
            HDData.house_id == house_id
            ).order_by(HDData.timestamp.desc()).first()

    if data_object == None:
        return None

    return (
            data_object.device_state,
            data_object.power_usage,
            data_object.temperature,
            data_object.timestamp
            )

def param_check(data: list[tuple[int, float, float, int]]) -> bool:
    """checks if max temperature is reached.

    Args:
        data (list[tuple[int, float, float, int]]): data

    Returns:
        bool:
    """
    curr_consumption = 0
    for house in data:
        curr_consumption += house[1]

    if curr_consumption >= params['max_usage'] * params['tolerance']:
        return False
    return True

def send_command() -> None:
    """send command to house subcontroller.

    Args:

    Returns:
        None:
    """
    global action_flag
    data_list = []
    ip_list = []
    id_list = []

    print('pre-for loop')
    for house in session.query(HousePool):
        data = get_data_from_house(house.id)
        if data == None:
            print('continues')
            continue

        data_list.append(data)
        ip_list.append(house.ip)
        id_list.append(house.id)

    print(id_list, ip_list)

    check_var = param_check(data_list)

    if check_var == action_flag:
        print('check_var = action_flag')
        return

    packet = ControlPacket()
    packet.add_devices(check_var, 1)

    for ip, house_id in zip(ip_list, id_list):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 42069))
        print('trying to send')
        sock.send(packet.get_packet())
        print('command successfully send')
        sock.close()

        action_entry = ActionPool(
                timestamp = time(),
                device = 1,
                state_change = check_var,
                house_id = house_id
                )

        session.add(action_entry)
        session.commit()

    action_flag = check_var
