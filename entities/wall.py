from utils import Object

import pygame


class Wall(Object):
    def __init__(self, screen: pygame.Surface, pos: pygame.Vector2, colour: tuple[int] = (255, 0, 255),) -> None:
        super().__init__("rectangle", pos, is_pushable=False, width=300, height=30)
        self.screen = screen
        self.colour = colour
        
    def draw(self, cam):
        pygame.draw.rect(
            self.screen,
            self.colour,
            pygame.Rect(
                (self.min_xy() * cam.zoom - cam.position).x,
                (self.min_xy() * cam.zoom - cam.position).y,
                self.width,
                self.height
            ),
        )
        