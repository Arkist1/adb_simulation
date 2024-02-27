import pygame
import objects
import math


class Bullet(objects.Object):
    def __init__(
        self, position, mouse_pos, bullet_speed=50, bullet_damage=50, screen=None
    ) -> None:
        super().__init__(position[0], position[1], 5)
        self.mouse_pos = mouse_pos
        self.speed = bullet_speed
        self.bullet_damage = bullet_damage
        self.screen = screen

        print(mouse_pos)
        neg_x = 1
        neg_y = 1
        dx = mouse_pos[0] - self.pos[0]
        dy = mouse_pos[1] - self.pos[1]
        if dx < 0:
            neg_x = -1
        if dy < 0:
            neg_y = -1
        sdelta = sum([abs(dx), abs(dy)])
        ratio = [abs(dx) / sdelta, abs(dy) / sdelta]
        velocity = (self.speed * ratio[0] * neg_x, self.speed * ratio[1] * neg_y)
        
        self.velocity = velocity

    def move(self, inputs):
        # print(self.aim)
        print(self.velocity)
        self.pos = (self.pos[0] + self.velocity[0] * inputs["dt"], self.pos[1] + self.velocity[1] * inputs["dt"] )

    def draw(self):
        pygame.draw.circle(self.screen, (0, 0, 0), self.pos, 5)

    def hit(self):
        pass
