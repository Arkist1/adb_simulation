from .bullet import Bullet

from utils import Globals

import math
import pygame


class Gun:
    """
    Represents a gun object in the game.

    Attributes:
        position (tuple): The position of the gun.
        fire_rate (int): The rate at which the gun can fire bullets.
        bullet_damage (int): The damage inflicted by each bullet.
        bullet_speed (int): The speed at which the bullets travel.
        hitbox (int): The size of the hitbox around the gun.
        img (pygame.Surface): The image of the gun.
        owner (Player): The owner of the gun.
        gunoffset (int): The offset of the gun from the owner's position.
        bullet_offset (int): The offset of the bullets from the gun's position.
        rect (pygame.Rect): The rectangle that represents the gun's position and size.
        screen (pygame.Surface): The screen on which the gun is drawn.
        rotation (float): The rotation angle of the gun.

    Methods:
        fire(): Fires a bullet from the gun.
        draw(): Draws the gun on the screen.
        rot_img(): Rotates the gun image based on the rotation angle.
        get_move(inputs): Calculates the rotation angle based on the mouse position.
        get_offset(offsetmulti): Calculates the offset vector based on the rotation angle.
    """

    def __init__(self, pos, screen: pygame.Surface = None):
        """
        Initializes a Gun object.

        Args:
            screen (pygame.Surface, optional): The screen surface to draw the gun on. Defaults to None.
            owner (Player, optional): The owner of the gun. Defaults to None.
        """
        self.position = None  # inherit from the player location
        self.fire_rate = 1000  # in miliseconds, 1000 = once every second
        self.bullet_damage = 50
        self.bullet_speed = 750
        self.bullet_size = 5

        # self.hitbox = 10 # not used
        self.img_size = pygame.Vector2(70, 70)
        self.img = pygame.transform.smoothscale(
            pygame.image.load(f"{Globals().root}/sprites/gun.png").convert_alpha(),
            self.img_size,
        )

        self.gunoffset = 30
        self.bullet_offset = 30

        self.rect = self.img.get_rect(center=pos)

        self.screen = screen
        self.rotation = 0

    def fire(self, from_pos, to_pos):
        """
        Fires a bullet from the gun.
        """
        return Bullet(
            from_pos,
            to_pos,
            rotation=self.rotation,
            offset=self.get_offset(2),
            bullet_speed=self.bullet_speed,
            bullet_damage=self.bullet_damage,
            bullet_size=self.bullet_size,
            screen=self.screen,
        )

    def draw(self, cam, pos):
        """
        Draws the gun on the screen.
        """
        rot_img = self.rot_img(cam, center_pos=pos)

        self.screen.blit(
            rot_img,
            self.rect,
        )

    def rot_img(self, cam, center_pos):
        """
        Rotates the gun image based on the rotation angle.

        Returns:
            pygame.Surface: The rotated gun image.
        """
        scaled_img = pygame.transform.smoothscale(self.img, self.img_size * cam.zoom)
        new_img = pygame.transform.rotate(scaled_img, self.rotation)

        self.rect = new_img.get_rect()
        # self.rect.w = self.rect.w / cam.zoom
        # self.rect.h = self.rect.h / cam.zoom

        self.rect.center = (
            center_pos * cam.zoom - cam.position + self.get_offset() * cam.zoom
        )  # / cam.zoom

        return new_img

    def get_move(self, inputs: dict, center_pos):
        """
        Calculates the rotation angle based on the mouse position.

        Args:
            inputs (dict): The input dictionary containing the mouse position.
        """
        v1 = center_pos - pygame.math.Vector2(inputs["mouse_pos"])
        v2 = pygame.math.Vector2([-100, 0])

        angle = v1.angle_to(v2)

        self.rotation = angle

    def get_offset(self, offsetmulti: int = 1):
        """
        Calculates the offset vector based on the rotation angle.

        Args:
            offsetmulti (int): The multiplier for the offset. Defaults to None.

        Returns:
            pygame.math.Vector2: The offset vector.
        """

        rads = math.radians(self.rotation)
        newvec = pygame.math.Vector2(math.cos(rads), -math.sin(rads)) * (
            offsetmulti * self.bullet_offset
        )

        return newvec
