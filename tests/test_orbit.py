import numpy as np
from loguru import logger
from matplotlib import pyplot as plt
from sgp4.api import Satrec

from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    z: float


class Vector(Point):
    pass


def create_corners(ax, size):
    """
    Plot corners to fix view
    :param ax: The current axis
    :param size: The absolute value max of a single direction from origin
    """
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-1, 1]:
                ax.plot([x * size], [y * size], [z * size], color="y")


def create_world(ax, earth_rad, scaling_factor, accuracy=20j):
    """
    Create a lattice representation of the earth
    :param ax: The current axis
    :param earth_rad: The radius of the earth
    :param scaling_factor: The scaling factor
    :param accuracy: The number of lattices
    """
    u, v = np.mgrid[0:2 * np.pi:accuracy, 0:np.pi:accuracy]
    x = np.cos(u) * np.sin(v) * earth_rad * scaling_factor
    y = np.sin(u) * np.sin(v) * earth_rad * scaling_factor
    z = np.cos(v) * earth_rad * scaling_factor
    ax.plot_wireframe(x, y, z, color="b")


def plot(ax, begin, end):
    """
    Plot a line from point_a to point_b
    :param ax: The current axis
    :param begin: Starting point
    :param end: End point
    """
    ax.plot(
        [begin.x, end.x],
        [begin.y, end.y],
        [begin.z, end.z],
        color="r"
    )


def loop(ax, starting_day, days, accuracy, fig, satellite):

    _prev_point = None
    iterations = days * accuracy  # days * accuracy

    for day in range(days):
        for i in range(accuracy):

            _day, _accuracy = starting_day + day, (1 / accuracy) * i
            logger.info(f"_day: {_day}\t _accuracy: {_accuracy}")
            # TODO Replace below with an actual simulation
            err, pos, vel = satellite.sgp4(_day, _accuracy)

            # parse current point
            curr_point = Point(x=pos[0], y=pos[1], z=pos[2])
            logger.info(f"Parsed point {curr_point}")

            # write previous point if not set
            if _prev_point is None:
                _prev_point = curr_point
                continue

            plot(ax, _prev_point, curr_point)

            # save current point as previous point
            _prev_point = curr_point

            # flush_events, draw canvas
            fig.canvas.flush_events()
            fig.canvas.draw()

            logger.info(f"Completed: {(i + 1) * (day + 1):05}/{iterations:05}")


def main():
    # set interactive mode to on
    plt.ion()

    # begin plot data
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    create_corners(ax, 7000)

    # draw earth
    earth_rad = 6371  # the radius of the earth
    scaling_factor = 0.8  # the scale that at which earth will be displayed
    create_world(ax, earth_rad, scaling_factor)

    # priming satellite data
    s = '1 25544U 98067A   21334.26436330  .00005004  00000-0  99898-4 0  9996'
    t = '2 25544  51.6438 241.5382 0004274 259.9657 242.7293 15.48711525314336'
    satellite = Satrec.twoline2rv(s, t)

    # system variables
    starting_day = 2458127  # Julian Date (Days since 12:00 January 1, 4713 BC)
    days = 14  # Days in this simulation
    accuracy = 2400  # Number of measured points per day

    # begin "simulation"
    loop(ax, starting_day, days, accuracy, fig, satellite)

    # turn off interactive mode
    plt.ioff()

    # show plot
    plt.show()


if __name__ == '__main__':
    main()
