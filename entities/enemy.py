from math import sqrt
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
        self.vision_cone.vision_range = 400

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

        self.vision_cone.get_move(self.poi)

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

            if sdelta < self.wanderspeed:  # detect if poi position is within reach
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

        self.move(pygame.Vector2(0, 0), entities)

    def detect_vision_cone_collision(self, agent):
        """
        Checks if the given agent is within the vision cone of this enemy.

        Args:
            agent (Agent): The agent to check for collision.

        Returns:
            bool: True if the agent is within the vision cone, False otherwise.
        """
        if (
            self.vision_cone.get_vision_cone_vertices() is None
            or agent.get_deteciton_circle() is None
        ):
            return False
        own_vertices = self.vision_cone.get_vision_cone_vertices()
        agent_center, agent_radius = agent.get_deteciton_circle()

        for vertex in own_vertices:
            if self.is_point_inside_circle(vertex, agent_center, agent_radius):
                return True
        return False

    def is_point_inside_circle(self, point, center, radius):
        return sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2) <= radius

    def percept(self):
        if self.state == "wandering" and not self.moving and self.move_timer <= 0:
            self.poi = pygame.Vector2(
                random.randrange(round(self.pos[0]) - 100, round(self.pos[0]) + 100),
                random.randrange(round(self.pos[1]) - 100, round(self.pos[1]) + 100),
            )
            self.moving = True

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Rotation": self.vision_cone.rotation,
            "Speed": self.speed,
            "POI": self.poi,
            "State": self.state,
            "Pushable": self.is_pushable,
        }
