from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
from sgp4.api import Satrec


# helper class for points
@dataclass
class Point:
    x: int
    y: int
    z: int


# set interactive mode to on
plt.ion()

# begin plot data
fig = plt.figure()
ax = fig.gca(projection='3d')

# set plot corners (to fix view)
size = 7000
for x in [-1, 1]:
    for y in [-1, 1]:
        for z in [-1, 1]:
            ax.plot([x * size], [y * size], [z * size], color="y")

# draw sphere
earth_rad = 6371  # the radius of the earth
scaling_factor = 0.8  # the scale that at which earth will be displayed
u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:20j]
x = np.cos(u) * np.sin(v) * earth_rad * scaling_factor
y = np.sin(u) * np.sin(v) * earth_rad * scaling_factor
z = np.cos(v) * earth_rad * scaling_factor
ax.plot_wireframe(x, y, z, color="b")

# priming satellite data
s = '1 25544U 98067A   19343.69339541  .00001764  00000-0  38792-4 0  9991'
t = '2 25544  51.6439 211.2001 0007417  17.6667  85.6398 15.50103472202482'
satellite = Satrec.twoline2rv(s, t)

# system variables
starting_day = 2465827  # Days since 12:00 January 1, 4713 BC
days = 14  # Days in this simulation
accuracy = 2400  # Number of measured points per day
iterations = days * accuracy  # days * accuracy

# establish previous point, defaulted None
_prev_point = None

for day in range(days):
    for i in range(accuracy):

        _day, _accuracy = starting_day + day, (1 / accuracy) * i
        logger.info(f"_day: {_day}\t _accuracy: {_accuracy}")
        # TODO Replace below with an actual simulation
        err, pos, vel = satellite.sgp4(_day, _accuracy)

        # parse current piont
        curr_point = Point(x=pos[0], y=pos[1], z=pos[2])
        logger.info(f"Parsed point {curr_point}")

        # write previous point if not set
        if _prev_point is None:
            _prev_point = curr_point
            continue

        # plot previous point -> new point
        ax.plot(
            [_prev_point.x, curr_point.x],
            [_prev_point.y, curr_point.y],
            [_prev_point.z, curr_point.z],
            color="r"
        )

        # save current point as previous point
        _prev_point = curr_point

        # flush_events, draw canvas
        fig.canvas.flush_events()
        fig.canvas.draw()

        logger.info(f"Completed: {(i+1)*(day+1):05}/{iterations:05}")

# turn off interactive mode
plt.ioff()

# show plot
plt.show()
