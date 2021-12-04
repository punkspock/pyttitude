import random
from dataclasses import dataclass

import numpy as np
import requests
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d


@dataclass  # dataclass wrapper
class Point:  # a position vector
    x: float
    y: float
    z: float

    def _str(self) -> str:
        return f"(x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f})"

    def __str__(self):
        return f"Point{self._str()}"


class Vector(Point):
    def __str__(self):
        return f"Vector{self._str()}"


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


def random_color():
    r = random.random()
    g = random.random()
    b = random.random()
    return r, g, b


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


class Arrow3D(FancyArrowPatch):
    """
    https://stackoverflow.com/a/22867877
    """
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)


def draw_arrow(ax, begin, end, color="r"):
    a = Arrow3D([begin.x, end.x], [begin.y, end.y],
                [begin.z, end.z], mutation_scale=5,
                lw=1, arrowstyle="-|>", color=color)
    ax.add_artist(a)
