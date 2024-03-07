from agent import Agent
import globals
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

        self.speed = self.speed / 2

    def get_move(self, inputs):
        """
        Determines the movement of the enemy based on the inputs.

        Args:
            inputs (dict): A dictionary containing input information.

        Returns:
            None
        """
        if self.controltype == "human":
            self.get_human_move(inputs)

        if self.controltype == "enemy":
            self.get_enemy_move(inputs)

    def get_enemy_move(self, inputs):
        """
        Calculates the movement of the enemy towards the nearest player.

        Args:
            inputs (dict): A dictionary containing input information.

        Returns:
            None
        """
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
