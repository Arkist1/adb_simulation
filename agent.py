import pygame
import globals


class Agent:
    def __init__(
        self, screen, start_pos=[250, 250], type="human", colour=(0, 0, 255)
    ) -> None:
        self.type = type
        self.speed = 300
        self.position = pygame.Vector2(start_pos)
        self.hitbox = 75
        self.colour = colour
        self.screen = screen

    def get_move(self, inputs):
        if self.type == "human":
            return self.get_human_move(inputs)

        if self.type == "random":
            return self.get_random_move()

    def get_random_move():
        return

    def get_human_move(self, inputs: dict[str, bool]) -> pygame.Vector2:
        s = self.speed * inputs["dt"]
        vec = pygame.Vector2(0, 0)

        if inputs["up"]:
            vec.y -= s
        if inputs["down"]:
            vec.y += s
        if inputs["left"]:
            vec.x -= s
        if inputs["right"]:
            vec.x += s

        if vec.x != 0 and vec.y != 0:
            vec.x /= globals.SQR2
            vec.y /= globals.SQR2

        self.position = self.position + vec

    def draw(self):
        pygame.draw.circle(
            self.screen, self.colour, self.position, self.hitbox
        )  # circle
