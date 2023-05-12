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

def get_data_from_houses() -> list[tuple[int, float, float, int, int]]:
    """function for getting data from house.

    Args:
        house_id (int): house_id

    Returns:
        tuple[int, float, float, int] | None:
    """
    data_list = []
    for house in session.query(HousePool):
        data_object = session.query(HDData).filter(
                HDData.house_id == house.id
                ).order_by(
                        HDData.timestamp.desc()
                        ).first()
        if data_object == None:
            continue

        data_list.append((data_object.device_state,
                          data_object.power_usage,
                          data_object.temperature,
                          data_object.timestamp,
                          data_object.house_id
                         ))
    return data_list

def param_check(data: list[tuple[int, float, float, int, int]]) -> bool | None:
    """checks if max temperature is reached.

    Args:
        data (list[tuple[int, float, float, int]]): data

    Returns:
        bool:
    """
    curr_consumption = 0
    for house in data:
        curr_consumption += house[1]

    if params['min_usage'] < curr_consumption < params['max_usage']:
        return None
    if curr_consumption >= params['max_usage']:
        return False
    return True

def send_command(off_houses: list) -> tuple[int, bool] | None:

    # variables
    prio_var: float = 0
    prio_ip: str | None = None
    prio: int | None = None
    house_data: list[tuple[int, float, float, int, int]] = get_data_from_houses()
    onoff: bool | None = param_check(house_data)

    if onoff == None:
        return

    # checks whether to turn utilities of or on
    if not onoff:

        # loops over data to find most suitable house to turn off
        for data in house_data:

            # filter out houses already turned off
            if data[4] in off_houses:
                continue

            if data[2] > prio_var:
                prio_var = data[2]
                prio = data[4]

    # else statement if utilities have to be turned on
    else:

        # filters data to find houses that are turned off
        filter_data = filter(lambda x: x[4] in off_houses, house_data)

        # find suitable house to turn on
        for data in filter_data:
            if data[2] < prio_var or prio_var == 0:
                prio_var = data[2]
                prio = data[4]

    if prio == None:
        print(f"No candidate send, command: {onoff}")
        return

    # find ip of house to take an action within
    house = session.query(HousePool).filter(HousePool.id == prio).first()
    if house != None:
        prio_ip = house.ip


    if prio_ip == None:
        print(f"Worst case: {prio} does have an ip")
        return

    # create packet
    packet = ControlPacket()
    packet.add_devices(onoff, 1)

    print(f'Trying to turn off {prio}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((prio_ip, 42069))
    sock.send(packet.get_packet())

    # ActionPool entry
    action_entry = ActionPool(
            timestamp = time(),
            device = 1,
            state_change = onoff,
            house_id = prio
            )

    session.add(action_entry)
    session.commit()

    return prio, onoff

    """
    LEGACY

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
    packet.print_packet()

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
    """
