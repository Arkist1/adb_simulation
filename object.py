from hitbox import Hitbox
import globals

import pygame

class Object(Hitbox):
    def __init__(
        self, 
        type_: str = "circle", 
        pos: pygame.Vector2 = pygame.Vector2(globals.MAP_WIDTH / 2, globals.MAP_HEIGHT / 2),
        min_pos: pygame.Vector2 = pygame.Vector2(0.0, 0.0),
        max_pos: pygame.Vector2 = pygame.Vector2(globals.MAP_WIDTH, globals.MAP_HEIGHT),
        is_movable: bool = True,
        **kwargs: float
    ) -> None:
        super().__init__(type_, pos, min_pos, max_pos, **kwargs)
        self.is_movable = is_movable
        
    def move(self, velocity: pygame.Vector2, objects: list[Hitbox]) -> bool:
        assert self.is_movable, "Object must have the is_movable=True flag to be able to be moved."
        
        new_pos = self.pos + velocity
        for object in objects:
            if self.is_colliding(object):
                return False
        self.pos = new_pos
        