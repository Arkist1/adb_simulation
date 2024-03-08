import pygame
from object import Object

class Wall(Object):
    def __init__(self, screen: pygame.Surface, pos: pygame.Vector2, colour: tuple[int] = (255, 0, 255),) -> None:
        super().__init__("rectangle", pos, is_pushable=False, width=80, height=10)
        self.screen = screen
        self.colour = colour
        
    def draw(self, cam):
        pygame.draw.rect(
            self.screen,
            self.colour,
            pygame.Rect(
                (self.pos * cam.zoom - cam.position).x - self.width / 2,
                (self.pos * cam.zoom - cam.position).y + self.height / 2,
                self.width,
                self.height
            ),
        )
        