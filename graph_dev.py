import matplotlib.pyplot as plt
from data_analysis import get_data_from_houses
import json
from models import HousePool, HDData
from utils import engine
from sqlalchemy.orm import sessionmaker

with open('anal_param.json', 'r') as fd:
    anal_params = json.load(fd)

y_max_value = anal_params["max_usage"]
y_min_value = anal_params["min_usage"]
max_cap = anal_params["max_capacity"]

y_max = []
y_min = []
x = []
y = []

def animate():
    global x
    global y
    data = get_data_from_houses()
    if len(data) > 0:
        x.append(data[0][3])
        consumption_sum = 0
        for tuple in data:
            consumption_sum += tuple[1]
        y.append(consumption_sum)
    else:
        x.append(0)
        y.append(0)


def live_graph():
    global x
    global y
    global y_max
    global y_min
    y_max = []
    y_min = []
    animate()
    for i in x:
        y_max.append(y_max_value)
        y_min.append(y_min_value)

    if len(x) > 1:
        if x[-1] // 3540 >=1 and x[-1] % 3540 == 0:
            plt.plot(x,y, '-b')
            plt.plot(x,y_max,'--r')
            plt.plot(x,y_min, '--y')
            plt.plot(x,y_min, '--m')
            plt.title("Power Consumption")
            plt.ylabel("kW")
            plt.xlabel("Seconds")
            name = f"graph_file_{x[-1]//3540}.png"
            plt.savefig(name, dpi=300)



def post_plot():
    Session = sessionmaker(bind = engine)
    session = Session()
    data_objects = session.query(HDData)
    if len(data_objects.all()) == 0:
        return
    
    y_list = []

    timestamps = [ts.timestamp for ts in data_objects.distinct(HDData.timestamp)]
    timestamps.sort()
    for stamp in timestamps:
        y = 0
        for data in data_objects.filter(HDData.timestamp == stamp):
            y += data.power_usage
        y_list.append(y)

    y_max = [y_max_value] * len(timestamps)
    y_min = [y_min_value] * len(timestamps)

    plt.plot(timestamps,y_list, '-b')
    plt.plot(timestamps,y_max,'--r')
    plt.plot(timestamps,y_min, '--y')
    plt.title("Power Consumption")
    plt.ylabel("kW")
    plt.xlabel("Seconds")
    name = f"graph_file.png"
    plt.savefig(name, dpi=300)


post_plot()