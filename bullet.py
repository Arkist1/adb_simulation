import pygame
import objects


class Bullet(objects.Object):
    def __init__(
        self, position, bullet_speed=600, bullet_damage=50, screen=None
    ) -> None:
        super().__init__(position[0], position[1], 5)
        self.speed = bullet_speed
        self.bullet_damage = bullet_damage
        self.screen = screen

    def move(self, inputs):
        self.pos[0] += self.speed + inputs["dt"]
        self.pos[1] += self.speed + inputs["dt"]

    def draw(self):
        pygame.draw.circle(self.screen, (0, 0, 0), self.pos, 5)

    def hit(self):
        pass
