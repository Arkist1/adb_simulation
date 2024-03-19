import pygame
from . import EntityHolder


class Tile(EntityHolder):
    def __init__(self, position, width, height) -> None:
        super().__init__()
        self.pos = position
        self.width = width
        self.height = height
        self.size = pygame.Vector2(self.width, self.height)
        self.rect = pygame.Rect(self.pos, self.size)
        
    def draw(self, screen, cam, col):
        pygame.draw.rect(
            screen,
            col,
            pygame.Rect(self.pos * cam.zoom - cam.position, self.size),
            #width=1
        ) 
