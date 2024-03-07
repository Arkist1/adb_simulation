import pygame
import math
from enum import Enum
import globals


def dist(p1: pygame.Vector2, p2: pygame.Vector2) -> float:
    """
    Calculate the Euclidean distance between two points.

    Args:
        p1 (pygame.Vector2): The first point.
        p2 (pygame.Vector2): The second point.

    Returns:
        float: The Euclidean distance between p1 and p2.
    """
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class HitboxType(Enum):
    """
    Enumeration class representing the types of hitboxes.
    
    Attributes:
        CIRCLE (int): Represents a circular hitbox.
        RECTANGLE (int): Represents a rectangular hitbox.
    """
    CIRCLE = 1
    RECTANGLE = 2


class Object:
    """
    Represents an object in the simulation.

    Args:
        pos_x (float): The x-coordinate of the object's position.
        pos_y (float): The y-coordinate of the object's position.
        width (float): The width of the object.
        height (float, optional): The height of the object. Defaults to None.

    Attributes:
        type (HitboxType): The type of hitbox for the object.
        width (float): The width of the object.
        height (float): The height of the object.
        radius (float): The radius of the object.
        max_x (float): The maximum x-coordinate value for the object's position.
        max_y (float): The maximum y-coordinate value for the object's position.
        pos (pygame.Vector2): The position of the object.

    Methods:
        hitbox_circle: Checks if the object's hitbox intersects with another object's hitbox (circle).
        hitbox_rectangle: Checks if the object's hitbox intersects with another object's hitbox (rectangle).
        move: Moves the object based on a given velocity and handles collision with other objects.
        hitbox_others: Checks for collision with other objects and handles collision resolution.

    """

    def __init__(
        self,
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
        """
        Checks if the object's hitbox intersects with another object's hitbox (circle).

        Args:
            other (Object): The other object to check collision with.

        Returns:
            bool: True if the hitboxes intersect, False otherwise.

        """
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
        """
        Checks if the object's hitbox intersects with another object's hitbox (rectangle).

        Args:
            other (Object): The other object to check collision with.

        Returns:
            bool: True if the hitboxes intersect, False otherwise.

        """
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
        """
        Moves the object based on a given velocity and handles collision with other objects.

        Args:
            velocity (pygame.Vector2): The velocity vector for the object.
            objects (list[any]): A list of other objects in the simulation.

        Returns:
            bool: True if a collision occurred, False otherwise.

        """
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
        """
        Checks for collision with other objects and handles collision resolution.

        Args:
            velocity (pygame.Vector2): The velocity vector for the object.
            objects (list[any]): A list of other objects in the simulation.
            temp (pygame.Vector2): The previous position of the object.

        Returns:
            bool: True if a collision occurred, False otherwise.

        """
        for object in objects:
            if object.type == HitboxType.CIRCLE:
                if object.hitbox_circle(self):
                    if self.type == HitboxType.CIRCLE:
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
            elif object.hitbox_rectangle(self):
                self.pos = temp
                return True
        return False
