import pygame
import globals
import object
import gun


class Agent(object.Object):
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
        self.weapon = gun.Gun(screen=self.screen, owner=self)

        self.health = health
        self.max_health = health
        self.food = food
        self.max_food = food
        self.stamina = stamina
        self.max_stamina = stamina

        self.is_moving = False

    def get_move(self, inputs: dict[str, bool]) -> pygame.Vector2:
        """
        Returns the move for the agent based on the given inputs.

        Args:
            inputs (dict[str, bool]): A dictionary containing the inputs for the agent.

        Returns:
            pygame.Vector2: The move for the agent.
        """
        if self.controltype == "human":
            return self.get_human_move(inputs)

        if self.controltype == "random":
            return self.get_random_move()

    def get_human_move(self, inputs: dict[str, bool]) -> pygame.Vector2:
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
            vec.x /= globals.SQR2
            vec.y /= globals.SQR2

        self.pos = self.pos + vec

        self.weapon.get_move(inputs)

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
        )  # circle
        if self.weapon:
            self.weapon.draw(cam)
