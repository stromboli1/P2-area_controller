import matplotlib.pyplot as plt
from data_analysis import get_data_from_houses
import json

with open('anal_param.json', 'r') as fd:
    anal_params = json.load(fd)

x_max_value = anal_params["max_usage"]
x_min_value = anal_params["min_usage"]

x_max = []
x_min = []
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
    global x_max
    global x_min
    animate()
    for i in y:
        x_max.append(x_max_value)
        x_min.append(x_min_value)
    print(y)
    print(x)
    print(x_max)
    print(x_min)
    plt.plot(x,y, '-b')
    #plt.plot(x_max,y,'--r')
    #plt.plot(x_min,y, '--y')
    plt.title("Power Consumption")
    plt.ylabel("kW")
    plt.xlabel("Seconds")
    
    if len(x) > 1:
        plt.savefig("graph_file.png")