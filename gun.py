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
        self.img = pygame.image.load(
            f"{globals.root}/sprites/agent_based_gun.png"
        ).convert_alpha()

        self.owner = owner
        self.screen = screen

    def fire(self):
        # on pressing initialize a bullet
        # projectile = bullet.Bullet(self.position, self.bullet_speed, self.bullet_damage)
        pass

    def draw(self):
        # load sprite
        self.screen.blit(self.img, self.owner.pos)
        # draw the gun on the screen
