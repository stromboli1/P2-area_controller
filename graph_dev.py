import matplotlib.pyplot as plt
from data_analysis import get_data_from_houses
import json

with open('anal_param.json', 'r') as fd:
    anal_params = json.load(fd)

x_max = anal_params["max_usage"]
x_min = anal_params["min_usage"]

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
    animate()
    plt.plot(x,y, '-b')
    plt.plot(x_max,y,'--r')
    plt.plot(x_min,y, '--y')
    plt.title("Power Consumption")
    plt.ylabel("kW")
    plt.xlabel("Seconds")
    
    if len(x) > 1:
        plt.savefig("graph_file.png")