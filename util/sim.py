import itertools
import random

from loguru import logger

from pyttitude.core import Pyttitude
from util import Point, plot, Vector, draw_arrow


class SatelliteSim:
    def __init__(self, ax, fig, env_, id_, sat, starting_day, color):
        self.ax = ax
        self.fig = fig
        self.env = env_
        self.id = id_
        self.satellite = sat
        self.starting_day = starting_day
        self.color = color
        self._iter_per_day = 1440
        self._prev_point = None
        self.action = env_.process(self.run())

    def run(self):
        while True:
            for day in itertools.count():
                for i in range(self._iter_per_day):

                    _day, _accuracy = self.starting_day + day, (1 / self._iter_per_day) * i
                    err, pos, vel = self.satellite.sgp4(_day, _accuracy)

                    # parse current point
                    curr_point = Point(x=pos[0], y=pos[1], z=pos[2])

                    # write previous point if not set
                    if self._prev_point is None:
                        self._prev_point = curr_point
                        continue

                    # draw orbit
                    plot(self.ax, self._prev_point, curr_point, self.color)

                    # save current point as previous point
                    self._prev_point = curr_point

                    # flush_events, draw canvas
                    self.fig.canvas.flush_events()
                    self.fig.canvas.draw()

                    logger.info(f"Completed {self.id} {(i + 1) * (day + 1):04}/{self._iter_per_day:04}")
                    yield self.env.timeout(1)


class SatelliteControl(SatelliteSim):  # SatelliteControl extends SatelliteSim

    def __init__(self, ax, fig, env_, id_, sat, starting_day, color):
        super().__init__(ax, fig, env_, id_, sat, starting_day, color)
        err, day_one, vel = self.satellite.sgp4(0, 0)
        self._sat_z_face = Vector(vel[0], vel[1], vel[2])
        self.pyttitude = Pyttitude(
            Point(day_one[0], day_one[1], day_one[2]),
            Vector(vel[0], vel[1], vel[2])
        )

    def run(self):
        while True:
            for day in itertools.count():
                for i in range(self._iter_per_day):

                    _day, _accuracy = self.starting_day + day, (1 / self._iter_per_day) * i
                    err, pos, vel = self.satellite.sgp4(_day, _accuracy)

                    # update pyttitude
                    self.pyttitude.update(pos=Point(pos[0], pos[1], pos[2]))

                    # https://numpy.org/doc/stable/reference/random/generated/numpy.random.binomial.html
                    # shuffle the satellite
                    vector = Vector(
                        self.pyttitude.z_face.x + random.randint(-700, 700),
                        self.pyttitude.z_face.y + random.randint(-700, 700),
                        self.pyttitude.z_face.z + random.randint(-700, 700)
                    )
                    self.pyttitude.update(face=vector)
                    logger.info(f"Updated sat with {vector}")

                    # current satellite +Z face, before adjustments
                    draw_arrow(
                        self.ax,
                        self.pyttitude.pos,
                        Point(self.pyttitude.pos.x + (self.pyttitude.z_face.x / 1),
                              self.pyttitude.pos.y + (self.pyttitude.z_face.y / 1),
                              self.pyttitude.pos.z + (self.pyttitude.z_face.z / 1)),
                        color="r"
                    )

                    # correct satellite :)
                    self.pyttitude.update(face=self.pyttitude.direction)

                    # parse current point
                    curr_point = Point(x=pos[0], y=pos[1], z=pos[2])

                    # write previous point if not set
                    if self._prev_point is None:
                        self._prev_point = curr_point
                        continue

                    # draw orbit
                    plot(self.ax, self._prev_point, curr_point, self.color)

                    # draw satellite +Z face, after adjustments
                    draw_arrow(
                        self.ax,
                        self.pyttitude.pos,
                        Point(self.pyttitude.pos.x + (self.pyttitude.z_face.x / 10),
                              self.pyttitude.pos.y + (self.pyttitude.z_face.y / 10),
                              self.pyttitude.pos.z + (self.pyttitude.z_face.z / 10)),
                        color="g"
                    )

                    # save current point as previous point
                    self._prev_point = curr_point

                    # flush_events, draw canvas
                    self.fig.canvas.flush_events()
                    self.fig.canvas.draw()

                    logger.info(f"Completed {self.id} {(i + 1) * (day + 1):04}/{self._iter_per_day:04}")
                    yield self.env.timeout(1)
