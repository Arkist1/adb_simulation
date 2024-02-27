import pygame
import bullet
import globals
import math


class Gun:
    def __init__(self, screen=None, owner=None):
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
        # on pressing initialize a bullet
        projectile = bullet.Bullet(self.position, self.bullet_speed, self.bullet_damage)

    def draw(self):
        # self.rotation = (self.rotation + 1) % 360
        # print(self.rotation)
        # self.screen.blit(self.img, self.owner.pos)

        rot_img = self.rot_img()
        self.screen.blit(rot_img, self.rect)

        # draw the gun on the screen

    def rot_img(self):

        # new_img = self.img.copy()
        # if 90 < self.rotation < 270:
        #     new_img = pygame.transform.flip(new_img, flip_x=1, flip_y=0)

        new_img = pygame.transform.rotate(self.img, self.rotation)

        self.rect = new_img.get_rect()
        self.rect.center = self.owner.pos + self.get_offset(self.gunoffset)

        return new_img

    def get_move(self, inputs):
        v1 = self.owner.pos - pygame.math.Vector2(inputs["mouse_pos"])
        v2 = pygame.math.Vector2([-100, 0])

        angle = v1.angle_to(v2)

        self.rotation = angle

    def get_offset(self, offsetmulti=None):
        if not offsetmulti:
            offsetmulti = self.owner.radius + self.bullet_offset
        rads = math.radians(self.rotation)
        newvec = pygame.math.Vector2(math.cos(rads), -math.sin(rads)) * (offsetmulti)

        return newvec
