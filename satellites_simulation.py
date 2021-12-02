import simpy
from loguru import logger
from matplotlib import pyplot as plt
from sgp4.api import Satrec

from config import earth_rad, scaling_factor, starting_day
from util import create_corners, create_world, fetch_satellites, random_color
from util.sim import SatelliteSim


def main():

    # set interactive mode to on
    plt.ion()  # enabling interactive mode

    # begin plot data
    fig = plt.figure()  # create figure
    ax = fig.gca(projection='3d')  # make 3D axis

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    create_corners(ax, 7000)  # place corners of View Cube (TM)

    # draw earth
    create_world(ax, earth_rad, scaling_factor, 20j)

    logger.info("Instantiating environment")
    env = simpy.Environment()

    logger.info("Fetching from celestrak...")
    satellites = fetch_satellites()

    logger.info("Loading satellites")
    for val in satellites:
        SatelliteSim(ax, fig, env, val["n"], Satrec.twoline2rv(val["s"], val["t"]), starting_day, random_color())

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
