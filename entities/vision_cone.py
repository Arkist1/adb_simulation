from utils import Object

import pygame
import math

class VisionCone:
    def __init__(self, screen: pygame.Surface = None, owner: any = None):
        self.position = None  # inherit from the player location
        self.owner = owner
        self.screen = screen
        self.vision_cone_vertices = None

        self.vision_range = 400
        self.vision_angle = 60
        self.rotation = 0
        self.offset = 1

    def draw(self, cam):
        """
        Draws the vision cone on the screen.

        """
        
        pos = (self.owner.pos * cam.zoom - cam.position)
        angle = self.rotation
        vision_range = self.vision_range
        vision_angle = self.vision_angle


        vertices = [
        pygame.math.Vector2(pos[0], pos[1]),
        pygame.math.Vector2(pos[0], pos[1]) + vision_range * pygame.math.Vector2(1, 0).rotate(angle - vision_angle / 2),
        pygame.math.Vector2(pos[0], pos[1]) + vision_range * pygame.math.Vector2(1, 0).rotate(angle + vision_angle / 2)
        ]

        pygame.draw.polygon(self.screen, (0, 0, 0), vertices, 1)
        self.vision_cone_vertices = vertices


    def get_move(self, inputs: dict):
        """
        Calculates the rotation angle based on the mouse position.

        Args:
            inputs (dict): The input dictionary containing the mouse position.
        """
        v1 = pygame.math.Vector2(inputs["mouse_pos"]) - self.owner.pos
        v2 = pygame.math.Vector2([0, 0])

        angle = v2.angle_to(v1)

        self.rotation = angle


    def get_offset(self, offsetmulti: int = None):
        """
        Calculates the offset vector based on the rotation angle.

        Args:
            offsetmulti (int): The multiplier for the offset. Defaults to None.

        Returns:
            pygame.math.Vector2: The offset vector.
        """
        rads = math.radians(self.rotation)
        newvec = pygame.math.Vector2(math.cos(rads), math.sin(rads)) * offsetmulti

        return newvec
    
    def get_vision_cone_vertices(self):
        return self.vision_cone_vertices