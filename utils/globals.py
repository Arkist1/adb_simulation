import os
import math
import pygame


class Globals:
    def __init__(self) -> None:
        pass

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    SCREEN_SIZE = pygame.Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)
    SQR2 = 2 ** (1 / 2)
    FPS = 60
    root = os.getcwd()
    MAP_WIDTH = 10_000
    MAP_HEIGHT = 7_000
    MAP_SIZE = pygame.Vector2(MAP_WIDTH, MAP_HEIGHT)
    FREECAM_SPEED = 1000
    DEBUG = True


def dist(p1: pygame.Vector2, p2: pygame.Vector2) -> float:
    """
    Calculate the Euclidean distance between two points.

    Args:
        p1 (pygame.Vector2): The first point.
        p2 (pygame.Vector2): The second point.

    Returns:
        float: The Euclidean distance between p1 and p2.
    """
    return math.sqrt(dist_sqr(p1, p2))


def dist_sqr(p1: pygame.Vector2, p2: pygame.Vector2) -> float:
    """
    Calculate the Euclidean distance squared between two points.

    Args:
        p1 (pygame.Vector2): The first point.
        p2 (pygame.Vector2): The second point.

    Returns:
        float: The Euclidean distance squared between p1 and p2.
    """
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return dx * dx + dy * dy
