from __future__ import annotations

from utils import Globals, Hitbox, dist, dist_sqr

import pygame


class Object(Hitbox):
    def __init__(
        self,
        type_: str = "circle",
        pos: pygame.Vector2 = pygame.Vector2(
            Globals().MAP_WIDTH / 2, Globals().MAP_HEIGHT / 2
        ),
        min_pos: pygame.Vector2 = pygame.Vector2(0.0, 0.0),
        max_pos: pygame.Vector2 = pygame.Vector2(
            Globals().MAP_WIDTH, Globals().MAP_HEIGHT
        ),
        **kwargs: float,
    ) -> None:
        super().__init__(type_, pos, min_pos, max_pos, **kwargs)

    def move(
        self, velocity: pygame.Vector2, objects: list[Object], is_chain: bool = False
    ) -> bool:
        if not self.enabled:
            return False
        
        self.pos += velocity

        w_off = self.radius if self.type == "circle" else self.width / 2
        h_off = self.radius if self.type == "circle" else self.height / 2

        if self.min_xy().x <= self.min_pos.x:
            self.pos.x = self.min_pos.x + w_off
        if self.max_xy().x >= self.max_pos.x:
            self.pos.x = self.max_pos.x - w_off
        if self.min_xy().y <= self.min_pos.y:
            self.pos.y = self.min_pos.y + h_off
        if self.max_xy().y >= self.max_pos.y:
            self.pos.y = self.max_pos.y - h_off

        colliding = []

        for other in objects:
            if other == self or not other.enabled:
                continue
            # if dist_sqr(self.pos, other.pos) > (self.max_xy().x - self.min_xy().x) ** 2:
            #    continue

            if self.is_colliding(other):
                if not other.is_pushable:
                    self.pos -= velocity

                    # if self.is_colliding(other):
                    #     vec = other.pos - self.pos
                    #     self.pos -= vec / 100
                    return False
                if not is_chain:
                    other.move(velocity * (2 / 3), objects, True)
                self.pos -= velocity * (1 / 3)
                colliding.append(other)

        if len(colliding) == 0:
            return True

        for other in colliding:
            if self.is_colliding(other):
                if self.type == "circle" and other.type == "circle":
                    perc = dist(self.pos, other.pos) / (self.radius + other.radius)
                    vec = other.pos - self.pos
                    if not is_chain:
                        other.move(vec / (50 * perc), objects, True)
                    self.pos -= vec / (50 * perc)
                else:
                    vec = other.pos - self.pos
                    if not is_chain:
                        other.move(vec / 300, objects, True)
                    self.pos -= vec / 300

        return True
