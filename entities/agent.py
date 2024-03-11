from .gun import Gun
from .vision_cone import VisionCone
from utils import Globals, Object

import pygame


class Agent(Object):
    """An agent instance"""

    def __init__(
        self,
        screen: pygame.Surface,
        start_pos: list[int] = [300, 300],
        type: str = "human",
        colour: tuple[int] = (0, 0, 255),
        size: int = 30,
        speed: int = 300,
        stamina: int = 250,
        food: int = 250,
        health: int = 250,
    ) -> None:
        super().__init__(pos=pygame.Vector2(start_pos[0], start_pos[1]), radius=size)
        self.controltype = type
        self.speed = speed
        self.hitbox = size
        self.colour = colour
        self.screen = screen
        self.weapon = Gun(screen=self.screen, owner=self)
        self.vision_cone = VisionCone(vision_range=700, screen=self.screen, owner=self)

        # hp
        self.health = health
        self.max_health = health

        # food/hunger
        self.food = food
        self.max_food = food
        self.hunger_rate = 2500

        # staminda
        self.stamina = stamina
        self.max_stamina = stamina
        self.stamina_cooldown = 1000

        # is moving flags
        self.is_crouching = False
        self.is_running = False

        self.cd = {"stamina_regen": 0, "food": 0}

        self.is_moving = False

    def get_move(self, inputs: dict[str, bool], entities) -> pygame.Vector2:
        """
        Returns the move for the agent based on the given inputs.

        Args:
            inputs (dict[str, bool]): A dictionary containing the inputs for the agent.

        Returns:
            pygame.Vector2: The move for the agent.
        """
        # generic move code
        for key, value in self.cd.items():
            if self.cd[key] >= 0:
                self.cd[key] = max(0, value - inputs["dt_mili"])

        print(self.cd["stamina_regen"])

        ### sprint and crouch ###
        if inputs["sprint"] and self.stamina > 0:
            self.stamina -= 1
            self.speed = 450
            self.cd["stamina_regen"] = self.stamina_cooldown
            self.is_running = True

        elif inputs["crouch"] and self.stamina > 0:
            self.stamina -= 0.5
            self.speed = 150
            self.is_crouching = True
            self.cd["stamina_regen"] = self.stamina_cooldown
        else:
            self.speed = 300

        ### stamina regen ###
        if self.cd["stamina_regen"] <= 0 and self.stamina < self.max_stamina:
            self.hunger_rate = 1000
            self.stamina = min(0.75 + self.stamina, self.max_stamina)

        else:
            self.hunger_rate = 2500

        ### hunger depletion ###
        if self.cd["food"] <= 0:
            self.cd["food"] = self.hunger_rate
            self.food -= 1
            if self.food <= 0:
                self.food = 0
                self.health -= 0.5

        if self.controltype == "human":
            return self.get_human_move(inputs, entities)

        if self.controltype == "random":
            return self.get_random_move()

    def get_human_move(self, inputs: dict[str, bool], entities) -> pygame.Vector2:
        """
        Calculates the movement vector based on the user inputs.

        Args:
            inputs (dict[str, bool]): A dictionary containing the user inputs.
                The keys represent the input types, and the values represent
                whether the input is active or not.

        Returns:
            pygame.Vector2: The movement vector calculated based on the user inputs.
        """
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
            vec.x /= Globals().SQR2
            vec.y /= Globals().SQR2

        # self.pos = self.pos + vec
        self.move(vec, entities)

        self.weapon.get_move(inputs)
        self.vision_cone.get_move(inputs["mouse_pos"])

    def shoot(self, location):
        if self.weapon:
            return self.weapon.fire(location)

    def draw(self, cam):
        """
        Draw the agent on the screen.

        This method draws a circle representing the agent on the screen using the specified colour and position.
        If the agent has a weapon, it also calls the `draw` method of the weapon to draw it on the screen.
        """
        pygame.draw.circle(
            self.screen,
            self.colour,
            self.pos * cam.zoom - cam.position,
            self.hitbox * cam.zoom,
        )  # circle (player)

        if self.controltype == "human":
            if self.is_crouching:
                pygame.draw.circle(
                    self.screen,
                    (0, 0, 0),
                    self.pos * cam.zoom - cam.position,
                    (self.hitbox + 100) * cam.zoom,
                    1,
                )  # crouching detection circle
                self.is_crouching = False
            elif self.is_running:
                pygame.draw.circle(
                    self.screen,
                    (0, 0, 0),
                    self.pos * cam.zoom - cam.position,
                    (self.hitbox + 400) * cam.zoom,
                    1,
                )  # running detection circle
                self.is_running = False
            else:
                pygame.draw.circle(
                    self.screen,
                    (0, 0, 0),
                    self.pos * cam.zoom - cam.position,
                    (self.hitbox + 200) * cam.zoom,
                    1,
                )  # base detection circle

        if self.weapon:
            self.weapon.draw(cam)

        if self.vision_cone:
            self.vision_cone.draw(cam)

    def get_debug_info(self):
        return {
            "Type": type(self).__name__,
            "Position": self.pos,
            "Rotation": self.vision_cone.rotation,
            "Speed": self.speed,
            "Crouching": self.is_crouching,
            "Running": self.is_running,
            "Food": self.food,
            "Health": self.health,
            "Stamina": self.stamina,
            "Pushable": self.is_pushable,
            "Hunger rate": self.hunger_rate,
        }
