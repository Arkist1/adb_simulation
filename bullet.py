import pygame

class Bullet:
    def __init__(self, position, bullet_speed, bullet_damage) -> None:
        self.possition = position
        self.speed = bullet_speed
        self.bullet_damage = bullet_damage

    def move(self):
        self.possition[0] += self.speed
        self.possition[1] += self.speed
        return self.possition

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.possition, 5)

    def hit(self):
        pass