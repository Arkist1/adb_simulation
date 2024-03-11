from utils import Object

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
        angle = self.rotation
        vision_range = self.vision_range * cam.zoom
        vision_angle = self.vision_angle

        vertices = [
            pygame.math.Vector2(pos[0], pos[1]),
            pygame.math.Vector2(pos[0], pos[1]) + vision_range * pygame.math.Vector2(1, 0).rotate(angle - vision_angle / 2),
            pygame.math.Vector2(pos[0], pos[1]) + vision_range * pygame.math.Vector2(1, 0).rotate(angle + vision_angle / 2),
        ]

        pygame.draw.polygon(self.screen, (0, 0, 0), vertices, 1)
        self.vision_cone_vertices = vertices

    def get_rotate_vision_cone(self, target: pygame.Vector2):
        """
        Calculates the rotation angle based on the mouse position.

        Args:
            inputs (dict): The input dictionary containing the mouse position.
        """
        v1 = pygame.math.Vector2(target) - self.owner.pos
        v2 = pygame.math.Vector2([0, 0])

        angle = v2.angle_to(v1)

        self.rotation = angle

    def get_vision_cone_info(self):
        return (self.vision_range, self.rotation)
