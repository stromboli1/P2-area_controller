import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sqlalchemy.orm import sessionmaker
from utils import engine
from models import HousePool, HDData
from data_analysis import get_data_from_houses

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
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    Session = sessionmaker(bind = engine)
    session = Session()

    ani = animation.FuncAnimation(fig, animate(), interval=200, frames=10)
    
    if len(x) > 1:
        ani.save('graph_file.mp4')