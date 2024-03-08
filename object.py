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
        **kwargs: float
    ) -> None:
        super().__init__(type_, pos, min_pos, max_pos, **kwargs)
        
    def move(self, velocity: pygame.Vector2, objects: list[Hitbox]) -> bool:
        self.pos += velocity
        w_off = (self.radius if self.type == "circle" else self.width / 2)
        h_off = (self.radius if self.type == "circle" else self.height / 2)
        
        if self.pos.x - w_off <= self.min_pos.x:
            self.pos.x = self.min_pos.x + w_off
        if self.pos.x + w_off >= self.max_pos.x:
            self.pos.x = self.max_pos.x - w_off
        if self.pos.y - h_off <= self.min_pos.y:
            self.pos.y = self.min_pos.y + h_off
        if self.pos.y + h_off >= self.max_pos.y:
            self.pos.y = self.max_pos.y - h_off
        
        for other in objects:
            if other == self:
                continue
            if self.is_colliding(other):
                if not other.is_pushable:
                    self.pos -= velocity
                    return False
                other.pos += velocity / 2
                self.pos -= velocity / 2
        
        for _ in range(100):
            any_colliding = False
            for other in objects:
                if other == self:
                    continue
                if self.is_colliding(other):
                    vec = other.pos - self.pos
                    other.pos += vec / 1000
                    any_colliding = True
            if not any_colliding:
                break
            
        return True
        