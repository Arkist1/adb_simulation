import pygame
import bullet
import globals
import math


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

    def __init__(self, screen: pygame.Surface = None, owner: any = None):
        """
        Initializes a Gun object.

        Args:
            screen (pygame.Surface, optional): The screen surface to draw the gun on. Defaults to None.
            owner (Player, optional): The owner of the gun. Defaults to None.
        """
        self.position = None  # inherit from the player location
        self.fire_rate = 1
        self.bullet_damage = 1
        self.bullet_speed = 5
        self.hitbox = 10
        self.img = pygame.transform.smoothscale(
            pygame.image.load(f"{globals.root}/sprites/gun.png").convert_alpha(),
            (70, 70),
        )

        self.owner = owner

        self.gunoffset = 30
        self.bullet_offset = 30

        self.rect = self.img.get_rect(center=owner.pos)

        self.screen = screen
        self.rotation = 0

    def fire(self):
        """
        Fires a bullet from the gun.
        """
        projectile = bullet.Bullet(self.position, self.bullet_speed, self.bullet_damage)

    def draw(self, cam_pos):
        """
        Draws the gun on the screen.
        """
        rot_img = self.rot_img()

        self.screen.blit(rot_img, self.rect.move(-cam_pos))

    def rot_img(self):
        """
        Rotates the gun image based on the rotation angle.

        Returns:
            pygame.Surface: The rotated gun image.
        """
        new_img = pygame.transform.rotate(self.img, self.rotation)

        self.rect = new_img.get_rect()
        self.rect.center = self.owner.pos + self.get_offset(self.gunoffset)

        return new_img

    def get_move(self, inputs: dict):
        """
        Calculates the rotation angle based on the mouse position.

        Args:
            inputs (dict): The input dictionary containing the mouse position.
        """
        v1 = self.owner.pos - pygame.math.Vector2(inputs["mouse_pos"])
        v2 = pygame.math.Vector2([-100, 0])

        angle = v1.angle_to(v2)

        self.rotation = angle

    def get_offset(self, offsetmulti: int = None):
        """
        Calculates the offset vector based on the rotation angle.

        Args:
            offsetmulti (int): The multiplier for the offset. Defaults to None.

        Returns:
            pygame.math.Vector2: The offset vector.
        """
        if not offsetmulti:
            offsetmulti = self.owner.radius + self.bullet_offset
        rads = math.radians(self.rotation)
        newvec = pygame.math.Vector2(math.cos(rads), -math.sin(rads)) * (offsetmulti)

        return newvec
