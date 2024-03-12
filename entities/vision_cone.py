from utils import Object
import utils
import math

import pygame


class VisionCone:
    def __init__(self, vision_range, screen: pygame.Surface = None, owner: any = None):
        self.position = None  # inherit from the player location
        self.owner = owner
        self.screen = screen
        self.vision_cone_vertices = None

        self.vision_range = vision_range
        self.vision_angle = 60
        self.rotation = 0

    def draw(self, cam):
        """
        Draws the vision cone on the screen.

        """

        pos = self.owner.pos * cam.zoom - cam.position
        vision_range = self.vision_range * cam.zoom
        vision_angle = self.vision_angle

        vertices = [
            pos,
            pos
            + vision_range
            * utils.angle_to_direction(math.radians(self.rotation - vision_angle / 2)),
            pos
            + vision_range
            * utils.angle_to_direction(math.radians(self.rotation + vision_angle / 2)),
        ]

        pygame.draw.polygon(self.screen, (0, 0, 0), vertices, 1)
        self.vision_cone_vertices = vertices

    def get_vision_cone_info(self):
        return (self.vision_range, self.rotation, self.vision_angle)
