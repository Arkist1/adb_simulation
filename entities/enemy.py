from .agent import Agent

import random
import pygame


class Enemy(Agent):
    """
    Represents an enemy agent in the game.

    Attributes:
        screen (pygame.Surface): The screen surface where the enemy is rendered.
        start_pos (list): The starting position of the enemy. Defaults to [250, 250].
        type (str): The type of the enemy. Defaults to None.
        colour (tuple): The colour of the enemy. Defaults to (255, 0, 0).
        weapon (object): The weapon object associated with the enemy.
        speed (float): The speed of the enemy.
    """

    def __init__(
        self, screen, start_pos=[250, 250], type=None, colour=(255, 0, 0)
    ) -> None:
        super().__init__(screen, start_pos, type=type, colour=colour)
        self.weapon = None
        self.poi = self.pos

        self.speed = self.speed / 2
        self.wanderspeed = self.speed / 4

        self.moving = False
        self.move_timer = 0
        self.state = "wandering"  # states are ["wandering", "alert", "chasing"]

    def get_move(self, inputs, entities):
        """
        Determines the movement of the enemy based on the inputs.

        Args:
            inputs (dict): A dictionary containing input information.

        Returns:
            None
        """
        if self.controltype == "human":
            self.get_human_move(inputs, entities)

        if self.controltype == "enemy":
            self.get_enemy_move(inputs, entities)

    def get_enemy_move(self, inputs, entities):
        """
        Calculates the movement of the enemy towards the nearest player.

        Args:
            inputs (dict): A dictionary containing input information.

        Returns:
            None
        """
        if self.move_timer > 0:
            self.move_timer -= inputs["dt"]

        elif self.state == "wandering":
            neg_x = 1
            neg_y = 1

            dx = self.poi[0] - self.pos[0]
            dy = self.poi[1] - self.pos[1]

            if dx < 0:
                neg_x = -1
            if dy < 0:
                neg_y = -1

            sdelta = sum([abs(dx), abs(dy)])

            if sdelta < self.wanderspeed:
                self.moving = False
                self.move_timer = random.random() * 2 + 2

            if not sdelta == 0:
                ratio = [abs(dx) / sdelta, abs(dy) / sdelta]

                delta = (
                    pygame.Vector2(
                        self.wanderspeed * ratio[0] * neg_x,
                        self.wanderspeed * ratio[1] * neg_y,
                    )
                    * inputs["dt"]
                )

                self.move(delta, entities)
                return

        # TODO: inplement
        # if self.state == "alert":

        # if self.state == "chasing":
        
        
        self.move(pygame.Vector2(0,0), entities)

    def percept(self):
        if self.state == "wandering" and not self.moving and self.move_timer <= 0:
            self.poi = pygame.Vector2(
                random.randrange(round(self.pos[0]) - 100, round(self.pos[0]) + 100),
                random.randrange(round(self.pos[1]) - 100, round(self.pos[1]) + 100),
            )
            self.moving = True
