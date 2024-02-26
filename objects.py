import pygame
import math
from enum import Enum
import globals


def dist(p1: pygame.Vector2, p2: pygame.Vector2) -> float:
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class HitboxType(Enum):
    CIRCLE = 1
    RECTANGLE = 2


class Object:
    def __init__(
        self,
        # max_x: float,
        # max_y: float,
        pos_x: float,
        pos_y: float,
        width: float,
        height: float = None,
    ) -> None:
        if height:
            self.type = HitboxType.RECTANGLE
            self.width = width
            self.height = height
        else:
            self.type = HitboxType.CIRCLE
            self.radius = width

        self.max_x = globals.SCREEN_WIDTH
        self.max_y = globals.SCREEN_HEIGHT
        self.pos = pygame.Vector2(pos_x, pos_y)

    def hitbox_circle(self, other):
        if self.type == HitboxType.CIRCLE:
            return dist(self.pos, other.pos) < (self.radius + other.radius)
        else:
            return not (
                self.pos.x + self.radius < (other.pos.x - (other.width / 2))
                or self.pos.x - self.radius > (other.pos.x + (other.width / 2))
                or self.pos.y + self.radius < (other.pos.y - (other.width / 2))
                or self.pos.y - self.radius > (other.pos.y + (other.width / 2))
            )

    def hitbox_rectangle(self, other):
        if self.type == HitboxType.CIRCLE:
            return not (
                self.pos.x + self.radius < (other.pos.x - (other.width / 2))
                or self.pos.x - self.radius > (other.pos.x + (other.width / 2))
                or self.pos.y + self.radius < (other.pos.y - (other.width / 2))
                or self.pos.y - self.radius > (other.pos.y + (other.width / 2))
            )
        else:
            return not (
                self.pos.x + (self.width / 2) < (other.pos.x - (other.width / 2))
                or self.pos.x - (self.width / 2) > (other.pos.x + (other.width / 2))
                or self.pos.y + (self.width / 2) < (other.pos.y - (other.width / 2))
                or self.pos.y - (self.width / 2) > (other.pos.y + (other.width / 2))
            )

    def move(self, velocity: pygame.Vector2, objects: list[any]):
        temp = pygame.Vector2(self.pos.x, self.pos.y)
        self.pos += velocity
        if self.type == HitboxType.RECTANGLE:
            if self.pos.x > self.max_x - self.width / 2:
                self.pos.x = self.max_x - self.width / 2
            if self.pos.x < self.width / 2:
                self.pos.x = self.width / 2
            if self.pos.y > self.max_y - self.height / 2:
                self.pos.y = self.max_y - self.height / 2
            if self.pos.y < self.height / 2:
                self.pos.y = self.height / 2
        elif self.type == HitboxType.CIRCLE:
            if self.pos.x > self.max_x - self.radius:
                self.pos.x = self.max_x - self.radius
            if self.pos.x < self.radius:
                self.pos.x = self.radius
            if self.pos.y > self.max_y - self.radius:
                self.pos.y = self.max_y - self.radius
            if self.pos.y < self.radius / 2:
                self.pos.y = self.radius / 2

        return self.hitbox_others(velocity, objects, temp)

    def hitbox_others(self, velocity: pygame.Vector2, objects: list[any], temp):
        for object in objects:
            if self.type == HitboxType.CIRCLE:
                if object.hitbox_circle(self):
                    if object.type == HitboxType.CIRCLE:
                        velocity_length = math.sqrt(velocity.x**2 + velocity.y**2)
                        if velocity_length == 0:
                            self.pos = temp
                            return True

                        max_length = dist(temp, object.pos) - (
                            self.radius + object.radius
                        )
                        self.pos = temp + (velocity * (max_length / velocity_length))
                    else:
                        self.pos = temp
                    return True
            else:
                if object.hitbox_rectangle(self):
                    self.pos = temp
                    return True
        return False
