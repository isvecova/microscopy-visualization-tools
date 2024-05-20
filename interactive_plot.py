import matplotlib
matplotlib.use('TkAgg')  # Ensures using a backend that supports interactivity

import numpy as np
import matplotlib.pyplot as plt

class InteractivePoints:
    def __init__(self, ax, point_size=100):
        self.ax = ax
        self.point_size = point_size
        self.points = []
        self.cid = ax.figure.canvas.mpl_connect('button_press_event', self)
        self.scatter = ax.scatter([], [], s=point_size)

    def __call__(self, event):
        if event.inaxes != self.ax:
            return
        self.points.append((event.xdata, event.ydata))
        self.scatter.set_offsets(self.points)
        self.ax.figure.canvas.draw()

fig, ax = plt.subplots()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
interactive_plot = InteractivePoints(ax, point_size=100)

plt.show()
