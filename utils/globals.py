import os
import math
import pygame


class Globals:
    def __init__(self) -> None:
        pass

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    SCREEN_SIZE = pygame.Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)

    MAP_WIDTH = SCREEN_WIDTH * 3
    MAP_HEIGHT = SCREEN_HEIGHT * 3
    MAP_SIZE = pygame.Vector2(MAP_WIDTH, MAP_HEIGHT)

    TILE_WIDTH = 1000
    TILE_HEIGHT = 700
    TILE_SIZE = pygame.Vector2(TILE_WIDTH, TILE_HEIGHT)

    SQR2 = 2 ** (1 / 2)
    root = os.getcwd()

    FREECAM_SPEED = 1000
    DEBUG = True
    DRAW = True

    CONTROL_TYPE = "agent"

    SIM_SPEED = 1
    FPS = 60 * SIM_SPEED

    RESTART = True


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


def angle_to(left: pygame.Vector2, right: pygame.Vector2) -> pygame.Vector2:
    v1 = left - right
    v2 = pygame.Vector2([0, 0])

    return v1.angle_to(v2)


def abs_distance_to(left, right):
    delta = left - right

    sdelta = sum([abs(delta[0]), abs(delta[1])])

    return sdelta


def angle_to_direction(angle: float):
    return pygame.math.Vector2(
        math.cos(angle), -math.sin(angle)
    )  # angle has to be in degrees
