from utils import Object

import pygame


class Bullet(Object):
    """
    Represents a bullet object in the game.

    Attributes:
        position (tuple): The initial position of the bullet.
        aim (tuple): The target position of the bullet.
        bullet_speed (int): The speed of the bullet.
        bullet_damage (int): The damage caused by the bullet.
        screen (pygame.Surface): The screen surface to draw the bullet on.
        owner (object): The owner of the bullet.

    Methods:
        __init__(self, position, aim, bullet_speed=50, bullet_damage=50, screen=None, owner=None)
            Initializes a new instance of the Bullet class.
        move(self, inputs)
            Moves the bullet based on the given inputs.
        draw(self)
            Draws the bullet on the screen.
        hit(self)
            Handles the bullet hit event.
        calc_velocity(self, aim)
            Calculates the velocity of the bullet based on the aim position.
    """

    def __init__(
        self,
        position,
        aim,
        rotation,
        offset,
        bullet_speed=50,
        bullet_damage=50,
        bullet_size=5,
        screen=None,
    ) -> None:
        """
        Initializes a Bullet object.

        Args:
            position (tuple): The initial position of the bullet.
            aim (tuple): The direction in which the bullet should travel.
            bullet_speed (int, optional): The speed of the bullet. Defaults to 50.
            bullet_damage (int, optional): The damage inflicted by the bullet. Defaults to 50.
            screen (object, optional): The screen object on which the bullet is displayed. Defaults to None.
            owner (object, optional): The object that owns the bullet. Defaults to None.
        """
        new_pos = position + offset
        super().__init__(pos=new_pos, radius=5)

        self.p_pos = position
        self.aim = aim
        self.speed = bullet_speed
        self.bullet_damage = bullet_damage
        self.bullet_size = bullet_size

        self.screen = screen
        self.velocity = self.calc_velocity(aim)
        self.rotation = rotation

    def move(self, inputs):
        """
        Moves the bullet based on the given inputs.

        Args:
            inputs (dict): The input values for the movement.

        Returns:
            None
        """
        self.pos = self.pos + self.velocity * inputs["dt"]

    def draw(self, cam):
        """
        Draws the bullet on the screen.

        Returns:
            None
        """
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            self.pos * cam.zoom - cam.position,
            self.bullet_size * cam.zoom,
        )

    def hit(self):
        """
        Handles the bullet hit event.

        Returns:
            None
        """
        pass

    def calc_velocity(self, aim):
        """
        Calculates the velocity of the bullet based on the aim position.

        Args:
            aim (tuple): The target position of the bullet.

        Returns:
            tuple: The velocity of the bullet.
        """
        neg_x = 1
        neg_y = 1
        dx = aim[0] - self.p_pos[0]
        dy = aim[1] - self.p_pos[1]
        if dx < 0:
            neg_x = -1
        if dy < 0:
            neg_y = -1
        sdelta = sum([abs(dx), abs(dy)])

        if sdelta == 0:
            ratio = [-1, 0]
        else:
            ratio = [abs(dx) / sdelta, abs(dy) / sdelta]
        return pygame.Vector2(
            self.speed * ratio[0] * neg_x, self.speed * ratio[1] * neg_y
        )

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Rotation": self.rotation,
            "Speed": self.speed,
            "Velocity": self.velocity,
            "Damage": self.bullet_damage,
        }
