import random
from dataclasses import dataclass

import numpy as np
import requests as requests
import simpy
from loguru import logger
from matplotlib import pyplot as plt
from sgp4.api import Satrec


@dataclass  # dataclass wrapper
class Point:  # a position vector
    x: float
    y: float
    z: float


class Vector(Point):
    pass


def create_corners(ax, size):
    """
    Plot corners to fix view. You're basically placing the corners of a cube.
    :param ax: The current axis in a matplotlib fig
    :param int size: The absolute value max of a single direction from origin
    """
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-1, 1]:
                ax.plot([x * size], [y * size], [z * size], color="y")


def create_world(ax, earth_rad, scaling_factor, accuracy=20j):
    """
    Create a lattice representation of the earth
    :param ax: The current axis
    :param int earth_rad: The radius of the earth
    :param float scaling_factor: The scaling factor
    :param complex accuracy: The number of lattices
    """
    u, v = np.mgrid[0:2 * np.pi:accuracy, 0:np.pi:accuracy]
    x = np.cos(u) * np.sin(v) * earth_rad * scaling_factor
    y = np.sin(u) * np.sin(v) * earth_rad * scaling_factor
    z = np.cos(v) * earth_rad * scaling_factor
    ax.plot_wireframe(x, y, z, color="b")


def plot(ax, begin, end, color):
    """
    Plot a line from point_a to point_b
    :param ax: The current axis
    :param Point begin: Starting point
    :param Point end: End point
    :param color: The color of this line
    """
    ax.plot(
        [begin.x, end.x],
        [begin.y, end.y],
        [begin.z, end.z],
        color=color
    )


def fetch_satellites():
    """
    Downloads the latest TLEs from CelesTrak
    :return: A list of TLE dictionaries
    """
    stations_url = "https://www.celestrak.com/NORAD/elements/stations.txt"
    stations = requests.get(stations_url).text.strip()

    def chunked(list_):
        for i in range(0, len(list_), 3):
            yield list_[i:i + 3]

    for line in chunked(stations.split('\r\n')):
        yield {
            "n": line[0],
            "s": line[1],
            "t": line[2]
        }


def main():

    # set interactive mode to on
    plt.ion()  # enabling interactive mode

    # begin plot data
    fig = plt.figure()  # create figure
    ax = fig.gca(projection='3d')  # make 3D axis

    create_corners(ax, 7000)  # place corners of View Cube (TM)

    # draw earth
    earth_rad = 6371  # the radius of the earth
    scaling_factor = 0.8  # the scale that at which earth will be displayed
    create_world(ax, earth_rad, scaling_factor)

    # system variables
    starting_day = 2459549  # Julian Date (Days since 12:00 January 1, 4713 BC)

    # Satellite object
    class Satellite:
        def __init__(self, env_, id_, sat, color):
            self.env = env_
            self.id = id_
            self.satellite = sat
            self.color = color
            self._iter_per_day = 1440
            self._prev_point = None
            self.action = env_.process(self.run())

        def run(self):
            while True:
                # TODO eventually replace day with something that works
                for day in range(10000):
                    for i in range(self._iter_per_day):

                        _day, _accuracy = starting_day + day, (1 / self._iter_per_day) * i
                        # TODO Replace below with an actual simulation
                        err, pos, vel = self.satellite.sgp4(_day, _accuracy)

                        # parse current point
                        curr_point = Point(x=pos[0], y=pos[1], z=pos[2])

                        # write previous point if not set
                        if self._prev_point is None:
                            self._prev_point = curr_point
                            continue

                        plot(ax, self._prev_point, curr_point, self.color)

                        # save current point as previous point
                        self._prev_point = curr_point

                        # flush_events, draw canvas
                        fig.canvas.flush_events()
                        fig.canvas.draw()

                        logger.info(f"Completed {self.id} {(i+1) * (day+1):04}/{self._iter_per_day:04}")
                        yield self.env.timeout(1)

    logger.info("Fetching from celestrak...")
    satellites = fetch_satellites()

    logger.info("Instantiating environment")
    env = simpy.Environment()

    def random_color():
        r = random.random()
        g = random.random()
        b = random.random()
        return r, g, b

    logger.info("Loading satellites")
    for val in satellites:
        Satellite(env, val["n"], Satrec.twoline2rv(val["s"], val["t"]), random_color())

    iterations = 10  # Run the simulation for 10 minutes
    logger.info(f"Begin simulation with {iterations} iterations")
    env.run(iterations)

    logger.info("Finished simulation")

    # turn off interactive mode
    plt.ioff()

    # show plot
    plt.show()


if __name__ == '__main__':
    main()
