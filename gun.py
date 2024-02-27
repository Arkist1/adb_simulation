import pygame
import bullet
import globals

class Gun:
    def __init__(self):
        self.position = None # inherit from the player location
        self.fire_rate = 1
        self.bullet_damage = 1
        self.bullet_speed = 5
        self.hitbox = 10
        self.img = pygame.image.load(f"{globals.root}/sprites/agent_based_gun.png").convert_alpha()

    def fire(self):
        #on pressing initialize a bullet
        # projectile = bullet.Bullet(self.position, self.bullet_speed, self.bullet_damage)
        pass
        

    def draw(self, screen):
        # load sprite
        screen.blit(self.img, self.position)
        #draw the gun on the screen