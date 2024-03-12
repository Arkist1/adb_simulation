from math import sqrt, atan2, degrees
import math
from .agent import Agent
from utils import Globals
import utils

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
        self.poi = self.pos  # Point Of Interest (POI)

        self.speed = self.speed / 2
        self.alertspeed = self.speed / 3
        self.wanderspeed = self.speed / 4

        self.moving = False
        self.move_timer = 0
        self.blocked_timer = 0
        self.state = "wandering"  # states are ["wandering", "alert", "chasing"]
        self.vision_cone.vision_range = 600
        self.detected_agent = []

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
        self.vision_cone.rotation = utils.angle_to(self.poi, self.pos)

        # if self.state == "chasing":
        #     self.poi = self.detected_agent

        if self.move_timer > 0:
            self.move_timer -= inputs["dt"]

        elif self.state == "wandering":
            self.blocked_timer -= inputs["dt"]

            sdelta = utils.abs_distance_to(self.pos, self.poi)
            # print(sdelta)

            if (
                sdelta < self.wanderspeed or self.blocked_timer <= 0
            ):  # detect if poi position is within reach
                self.moving = False
                self.move_timer = random.random() * 2 + 2
                self.blocked_timer = random.random() * 2 + 2

            if not sdelta == 0:
                # calculate delta
                angle = utils.angle_to(self.pos, self.poi)
                delta = (
                    utils.angle_to_direction(angle) * self.wanderspeed * inputs["dt"]
                )

                self.move(delta, entities)
                return

        
        elif self.state == "alert":
            angle = self.angle_to(self.poi)
            delta = self.angle_to_direction(angle) * self.speed * inputs["dt"]

            self.move(delta, entities)
        # TODO: inplement
        # if self.state == "chasing":

        self.move(pygame.Vector2(0, 0), entities)

    def percept(self, entities):
        """
        Checks if the given agent is within the vision cone of this enemy.

        Args:
            agent (Agent): The agent to check for collision.

        Returns:
            bool: True if the agent is within the vision cone, False otherwise.
        """
        detections = []
        for entity in entities:
            if self.detect(entity):
                detections.append(entity)

        if detections:
            print("detection has been made")
            print(detections[0].pos)
            self.state = "alert"
            self.poi = detections[0].pos

        else:
            self.state = "wandering"

            if (
                not self.moving and self.move_timer <= 0
            ):  # Only get new poi if old one has been reached
                self.poi = pygame.Vector2(
                    random.randrange(
                        round(self.pos[0]) - 100, round(self.pos[0]) + 100
                    ),
                    random.randrange(
                        round(self.pos[1]) - 100, round(self.pos[1]) + 100
                    ),
                )
                self.moving = True

        self.detected_agents = detections

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Rotation": self.vision_cone.rotation,
            "Speed": self.speed,
            "POI": self.poi,
            "Blocked_timer": self.blocked_timer,
            "move_timer": self.move_timer,
            "State": self.state,
            "Pushable": self.is_pushable,
        }
