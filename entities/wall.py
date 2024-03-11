from utils import Object

import pygame


class Wall(Object):
    def __init__(
        self,
        screen: pygame.Surface,
        pos: pygame.Vector2,
        width: int = 300,
        height: int = 30,
        colour: tuple[int] = (255, 0, 255),
    ) -> None:
        super().__init__("rectangle", pos, is_pushable=False, width=width, height=height)
        self.screen = screen
        self.colour = colour

    def draw(self, cam):
        pygame.draw.rect(
            self.screen,
            self.colour,
            pygame.Rect(
                (self.min_xy() * cam.zoom - cam.position).x,
                (self.min_xy() * cam.zoom - cam.position).y,
                self.width * cam.zoom,
                self.height * cam.zoom,
            ),
        )

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Width": self.width,
            "Height": self.height,
            "Pushable": self.is_pushable,
        }
