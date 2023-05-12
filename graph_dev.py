import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sqlalchemy.orm import sessionmaker
from utils import engine
from models import HousePool, HDData
from data_analysis import get_data_from_houses


def animate(i, x, y):
    data = get_data_from_houses()
    x.append(data[0][3])
    consumption_sum = 0
    for tuple in data:
        consumption_sum += tuple[1]
    y.append(consumption_sum)

def live_graph():
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    x = []
    y = []

    Session = sessionmaker(bind = engine)
    session = Session()

    ani = animation.FuncAnimation(fig, animate(x=x,y=y), interval=200, frames=10)
    plt.savefig('graph_file.png')