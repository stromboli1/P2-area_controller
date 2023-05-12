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

def send_command(off_houses: list) -> tuple[int, bool] | tuple[int, int] | None:

    # variables
    prio_var: float = 0
    prio_ip: str | None = None
    prio: int | None = None
    house_data: list[tuple[int, float, float, int, int]] = get_data_from_houses()
    onoff: bool | None = param_check(house_data)

    if onoff == None:
        if len(off_houses) == 0 or len(off_houses) == len(house_data):
            return
        switch_var = switch(house_data, off_houses)
        if switch_var == None:
            return
        return switch_var

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

    print(f"Command for {prio}, command: {onoff}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((prio_ip, 42069))
    sock.send(packet.get_packet())
    sock.close()

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

def switch(data_list: list[tuple[int, float, float, int, int]], off_houses: list) -> tuple[int, int] | None:

    # variables
    prio_var = 0
    prio = None
    cand_var = 0
    cand = None

    for data in data_list:
        if data[4] not in off_houses:
            if data[2] > cand_var:
                cand_var = data[2]
                cand = data[4]
        else:
            if data[2] < prio_var:
                prio_var = data[2]
                prio = data[4]

    if prio == None or cand == None:
        return

    if cand_var < prio_var:
        return

    houses = session.query(HousePool)
    cand_data = houses.filter(HousePool.id == cand).first()
    prio_data = houses.filter(HousePool.id == prio).first()

    if cand_data == None or prio_data == None:
        return

    # create packets and sockets and send

    packet = ControlPacket()
    packet.add_devices(False, 1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((cand_data.ip, 42069))
    sock.send(packet.get_packet())
    sock.close()

    packet.add_devices(True, 1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((prio_data.ip, 42069))
    sock.send(packet.get_packet())
    sock.close()

    # create action entry

    action_entry_cand = ActionPool(
            timestamp = time(),
            device = 1,
            state_change = False,
            house_id = cand
            )

    action_entry_prio = ActionPool(
            timestamp = time(),
            device = 1,
            state_change = True,
            house_id = prio
            )

    session.add_all([action_entry_cand, action_entry_prio])
    session.commit()

    return prio, cand
