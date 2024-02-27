from agent import Agent
import globals
import pygame


class Enemy(Agent):
    def __init__(
        self, screen, start_pos=[250, 250], type=..., colour=(255, 0, 0)
    ) -> None:
        super().__init__(screen, start_pos, type=type, colour=colour)
        self.weapon = None

        self.speed = self.speed / 2

    def get_move(self, inputs):
        if self.controltype == "human":
            self.get_human_move(inputs)

        if self.controltype == "enemy":
            self.get_enemy_move(inputs)

    def get_enemy_move(self, inputs):
        player_delta = self.pos - inputs["nearest_player"].pos

        neg_x = -1
        neg_y = -1

        if player_delta[0] < 0:
            neg_x = 1
        if player_delta[1] < 0:
            neg_y = 1

        sdelta = sum([abs(player_delta[0]), abs(player_delta[1])])
        ratio = [abs(player_delta[0]) / sdelta, abs(player_delta[1]) / sdelta]

        new_pos = pygame.Vector2(
            ratio[0] * self.speed * inputs["dt"] * neg_x,
            ratio[1] * self.speed * inputs["dt"] * neg_y,
        )

        self.move(new_pos, [inputs["nearest_player"]])
