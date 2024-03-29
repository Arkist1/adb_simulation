from __future__ import annotations
from utils import Globals, dist

import pygame


class Hitbox:
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
        is_pushable: bool = True,
        enabled: bool = True,
        **kwargs: float,
    ) -> None:
        if type_ not in ["circle", "rectangle"]:
            raise ValueError(
                f"Type of Hitbox must be 'circle' or 'rectrangle' not '{type_}'."
            )

        self.type = type_
        self.pos = pos
        self.min_pos = min_pos
        self.max_pos = max_pos
        self.is_pushable = is_pushable
        self.enabled = enabled

        if type_ == "circle":
            if "radius" not in kwargs:
                raise ValueError("Hitbox of type 'circle' must have a 'radius': float.")
            self.radius = kwargs["radius"]

        if type_ == "rectangle":
            if "width" not in kwargs or "height" not in kwargs:
                raise ValueError(
                    "Hitbox of type 'rectangle' must have a 'width': float and 'height': float."
                )
            self.width = kwargs["width"]
            self.height = kwargs["height"]

    def min_xy(self) -> pygame.Vector2:
        if self.type == "circle":
            return pygame.Vector2(self.pos.x - self.radius, self.pos.y - self.radius)
        return pygame.Vector2(
            self.pos.x - (self.width / 2), self.pos.y - (self.height / 2)
        )

    def max_xy(self) -> pygame.Vector2:
        if self.type == "circle":
            return pygame.Vector2(self.pos.x + self.radius, self.pos.y + self.radius)
        return pygame.Vector2(
            self.pos.x + (self.width / 2), self.pos.y + (self.height / 2)
        )

    def is_colliding(self, other: Hitbox) -> bool:
        if self.type == "circle" and other.type == "circle":
            return dist(self.pos, other.pos) < (self.radius + other.radius)
        return self.is_hitbox_within(other.min_xy(), other.max_xy())

    def is_hitbox_within(
        self, min_coords: pygame.Vector2, max_coords: pygame.Vector2
    ) -> bool:
        is_x_within = self.max_xy().x > min_coords.x and self.min_xy().x < max_coords.x
        is_y_within = self.max_xy().y > min_coords.y and self.min_xy().y < max_coords.y
        return is_x_within and is_y_within
