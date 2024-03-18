import pygame
from . import EntityHolder


class Tile(EntityHolder):
    def __init__(self, position, width, height) -> None:
        super().__init__()
        self.pos = position
        self.width = width
        self.height = height
        self.size = pygame.Vector2(self.width, self.height)
