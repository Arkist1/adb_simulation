class Agent:
    def __init__(self) -> None:
        self.type = "human"
        self.root2 = 2**1 / 2

    def move(self, inputs):
        if self.type == "human":
            return self.get_human_move(inputs)

        if self.type == "random":
            return self.get_random_move()

    def get_random_move():
        return

    def get_human_move(self, inputs):
        delta = [0, 0]  # [x, y]
        total_inputs = 0
        if inputs["up"]:
            total_inputs += 1
            delta[1] -= 5

        if inputs["down"]:
            total_inputs += 1
            delta[1] += 5

        if inputs["left"]:
            total_inputs += 1
            delta[0] -= 5

        if inputs["right"]:
            total_inputs += 1
            delta[0] += 5

        if total_inputs > 2:
            delta[0] = delta[0] / self.root2
            delta[1] = delta[1] / self.root2
