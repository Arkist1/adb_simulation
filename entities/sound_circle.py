from utils import Object
import utils
import math

import pygame


class SoundCircle:
    def __init__(self, sound_range, screen: pygame.Surface = None, owner: any = None):
        self.position = None  # inherit from the player location
        self.owner = owner
        self.screen = screen

        self.sound_range = sound_range

    def draw(self, cam):
        """
        Draws the sound cone on the screen.

        """
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            self.owner.pos * cam.zoom - cam.position,
            (self.sound_range) * cam.zoom,
            1,
        )

    def get_vision_cone_info(self):
        return (self.vision_range, self.rotation, self.vision_angle)
