# imports
import numpy as np
# import astropy as ap
from loguru import logger
from matplotlib import pyplot as plt
from sgp4.api import Satrec
from astropy.coordinates import cartesian_to_spherical, spherical_to_cartesian

from dataclasses import dataclass

# constants
earth_radius = 6371


""" shorthand for instantiating an object that is really just a
container of data. """
@dataclass  # dataclass wrapper
class Cartesian:  # a position vector  # point
    x: float
    y: float
    z: float

    # holy shit
    def spherical(self):
        return cartesian_to_spherical(self.x, self.y, self.z)


@dataclass
class Spherical:  # a position vector  # point
    r: float
    theta: float
    phi: float

    def cartesian(self):
        return spherical_to_cartesian(self.r, self.theta, self.phi)


# This is just here so Nick could show me what he was talking about lol
class Vector(Cartesian):
    pass


@dataclass
class Sat:
    point: Spherical  # where it is  # can be spherical or cartesian
    vector: Vector  # where it's going  # idk man
    inclination: Theta  # is this necessary?  # degrees


#
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


def radial(earth_radius, theta, eccentricity):
    """
    Radial distance as a function of radius of the earth, polar angle, and eccentricity.
    :param radius: float in meters.
    :param theta: float in degrees.
    :param eccentricity: float.
    :return:
    """
    r_theta = (earth_radius * (1 - e**2)) / (1 + e * np.cos(theta))

    return r_theta


# propagation function
# object -> needs to be calculated
# time unit -> how long tho?
# vectors -> List[Vectors]

# TODO: make this a method that belongs to the satellite class
def propagate(satellite):
    """

    :param Sat satellite: Satellite object with point and vector.
    :return:
    """


    from_ = satellite.point  # where it's coming from
    to_ = satellite.vector  # where it's going


    orbit_theta = 90.00 - satellite.inclination  # in degrees
    orbit_radius = radial(satellite.inclination) # point
    orbit_phi =  # here's where I get lost
    satellite.vector = (orbit_radius, orbit_theta, orbit_phi)  # vector
    return


# reStructuredText
def car(env):
    """

    :param simpy.core.Environment env: SimPy environment
    :return:
    """
    while True:
        print('Start parking at %d' % env.now)
        parking_duration = 5
        yield env.timeout(parking_duration)

        print('Start driving at %d' % env.now)
        trip_duration = 2
        yield env.timeout(trip_duration)


# Satellite object
class Satellite:
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.run())

    def run(self):
        while True:
            print("Start orbit at {}".format(self.env.now))  # simpy.Environment.now is a Thing(TM)
            orbit_duration = 1  # minutes
            yield self.env.timeout(orbit_duration)

            # recalculate position every minute. 90 minutes to an orbit.
            # only think about gravity for right now


# >>> import simpy
# >>> env = simpy.Environment()
# >>> env.process(car(env))
# <Process(car) object at 0x...>
# env.run(until=15)
# parked 1: 0
# parked 2: 0
# drivin 1: 5
# drivin 2: 5
# parked 1: 7
# parked 2: 7
# drivin 1: 12
# drivin 2: 12
# parked 1: 14
# parked 2: 14


def plot(ax, begin, end):
    """
    Plot a line from point_a to point_b
    :param ax: The current axis
    :param Point begin: Starting point
    :param Point end: End point
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
            curr_point = Cartesian(x=pos[0], y=pos[1], z=pos[2])
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
    plt.ion()  # enabling interactive mode

    # begin plot data
    fig = plt.figure()  # create figure
    ax = fig.gca(projection='3d')  # make 3D axis

    create_corners(ax, 7000)  # place corners of View Cube (TM)

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
