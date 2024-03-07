import os
import math
import pygame

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SQR2 = 2 ** (1 / 2)
FPS = 240
root = os.getcwd()
MAP_WIDTH = 1000
MAP_HEIGHT = 700

def dist(p1: pygame.Vector2, p2: pygame.Vector2) -> float:
    """
    Calculate the Euclidean distance between two points.

    Args:
        p1 (pygame.Vector2): The first point.
        p2 (pygame.Vector2): The second point.

    Returns:
        float: The Euclidean distance between p1 and p2.
    """
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)