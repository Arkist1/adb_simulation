import pygame
import objects
import math


class Bullet(objects.Object):
    def __init__(
        self, position, aim, counting, bullet_speed=50, bullet_damage=50, screen=None
    ) -> None:
        offset = owner.get_offset()
        new_pos = position + offset
        super().__init__(*new_pos, 5)
        self.aim = aim
        self.speed = bullet_speed
        self.bullet_damage = bullet_damage
        self.screen = screen
        self.velocity = self.calc_velocity(aim)

        self.counting = counting

    def move(self, inputs):
        # print(self.aim)
        self.pos = (
            self.pos[0] + self.velocity[0] * inputs["dt"],
            self.pos[1] + self.velocity[1] * inputs["dt"],
        )

    def draw(self):
        # pygame.draw.circle(self.screen, (0, 0, 0), self.pos, 5)
        
        black = (0, 0, 0)
        font = pygame.font.SysFont('Comic Sans MS', 36)
        text = font.render("HelloWorld!"[self.counting], True, black, None)
        textRect = text.get_rect()
        textRect.center = (self.pos)
        self.screen.blit(text, textRect)

    def hit(self):
        pass

    def calc_velocity(self, aim):
        neg_x = 1
        neg_y = 1
        dx = aim[0] - self.pos[0]
        dy = aim[1] - self.pos[1]
        if dx < 0:
            neg_x = -1
        if dy < 0:
            neg_y = -1
        sdelta = sum([abs(dx), abs(dy)])
        ratio = [abs(dx) / sdelta, abs(dy) / sdelta]
        return (self.speed * ratio[0] * neg_x, self.speed * ratio[1] * neg_y)
