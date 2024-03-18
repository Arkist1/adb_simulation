import utils
from utils import Globals

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import math
import pygame


class Sword:

    def __init__(self, owner, screen: pygame.Surface = None):
        self.position = None  # inherit from the player location
        self.fire_rate = 300  # in miliseconds, 1000 = once every second
        self.cd = 0
        self.damage = 25
        self.sword_size = 100
        self.size = 0
        self.angle = 180
        self.rotation = 0
        self.duration = 90
        self.duration_cd = 0
        self.did_damage = False

        self.owner = owner
        self.screen = screen

    def swing(self, to_pos):
        self.rotation = utils.angle_to(to_pos, self.owner.pos)
        self.size = 100
        return

    def draw(self, cam, pos):
        pos = pos * cam.zoom - cam.position
        range = self.size * cam.zoom

        vertices = self.get_shape(pos, range)

        pygame.draw.polygon(self.screen, (0, 0, 0), vertices, 1)

    def get_shape(self, pos, range):
        return [
            pos,
            pos
            + 0.75
            * range
            * utils.angle_to_direction(math.radians(self.rotation - self.angle / 2)),
            pos
            + 2
            * range
            / 2
            * utils.angle_to_direction(math.radians(self.rotation - self.angle / 6)),
            pos
            + 2
            * range
            / 2
            * utils.angle_to_direction(math.radians(self.rotation + self.angle / 6)),
            pos
            + 0.75
            * range
            * utils.angle_to_direction(math.radians(self.rotation + self.angle / 2)),
        ]

    def hit(self, entity):
        en_pos = entity.pos
        shape = self.get_shape(self.owner.pos, self.size)
        return Point(en_pos).within(Polygon(shape))
