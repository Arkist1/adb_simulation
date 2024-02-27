import pygame
import bullet
import globals


class Gun:
    def __init__(self, screen=None, owner=None):
        self.position = None  # inherit from the player location
        self.fire_rate = 1
        self.bullet_damage = 1
        self.bullet_speed = 5
        self.hitbox = 10
        self.img = pygame.transform.smoothscale(
            pygame.image.load(
                f"{globals.root}/sprites/agent_based_gun.png"
            ).convert_alpha(),
            (100, 100),
        )
        self.owner = owner

        print(owner.pos)
        self.rect = self.img.get_rect(center=owner.pos)

        self.screen = screen
        self.rotation = 90

    def fire(self):
        # on pressing initialize a bullet
        projectile = bullet.Bullet(self.position, self.bullet_speed, self.bullet_damage)

    def draw(self):
        # # load sprite
        # self.rotation += 1
        # self.rotation = self.rotation % 360
        # print(self.rotation)

        # self.rot_img()
        # self.screen.blit(self.img, self.rect)
        self.screen.blit(self.img, self.owner.pos)
        # draw the gun on the screen

    def rot_img(self):
        self.img = pygame.transform.rotate(self.img, self.rotation)
        self.rect.center = self.owner.pos
