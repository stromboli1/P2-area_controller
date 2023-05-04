# imports
import json
from sqlalchemy.orm import sessionmaker
from models import HousePool, HDData, ActionPool
from utils import engine
from control_protocol import ControlPacket

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

    return (
            data_object.device_state,
            data_object.power_usage,
            data_object.temperature,
            data_object.timestamp
            )

def param_check(data: list[tuple[int, float, float, int]]) -> bool:
    curr_consumption = 0
    for house in data:
        curr_consumption += house[1]

    if curr_consumption >= params['max_usage'] * params['tolerance']:
        return False
    return True
