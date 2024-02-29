import pygame
import globals
import objects
import gun


class Agent(objects.Object):
    """An agent instance
    """    
    def __init__(
        self,
        screen: pygame.Surface,
        start_pos: list[int] = [300, 300],
        type: str = "human",
        colour: tuple[int] = (0, 0, 255),
        size: int = 30,
        speed: int = 300,
    ) -> None:
        """Create an agent object

        Args:
            screen (pygame.Surface): The screen to draw the agent to
            start_pos (list[int], optional): Starting position [x, y]. Defaults to [300, 300].
            type (str, optional): The type of agent "human", "random". Defaults to "human".
            colour (tuple[int], optional): The color of the agent (r, g, b). Defaults to (0, 0, 255).
            size (int, optional): The size of the agent. Defaults to 30.
            speed (int, optional): The movement speed of the agent. Defaults to 300.
        """               
        super().__init__(pos_x=start_pos[0], pos_y=start_pos[1], width=size)
        self.controltype = type
        self.speed = speed
        self.hitbox = size
        self.colour = colour
        self.screen = screen
        self.weapon = gun.Gun(screen=self.screen, owner=self)

    def get_move(self, inputs):
        if self.controltype == "human":
            return self.get_human_move(inputs)

        if self.controltype == "random":
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

        self.pos = self.pos + vec

        self.weapon.get_move(inputs)
        # bullets don't move
        # if inputs["shoot"]:
        #     self.weapon.fire()

    def draw(self):
        pygame.draw.circle(self.screen, self.colour, self.pos, self.hitbox)  # circle
        if self.weapon:
            self.weapon.draw()
