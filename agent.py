class Agent:
    def __init__(self) -> None:
        self.type = "human"
        self.root2 = 2 ** (1 / 2)

    def get_move(self, inputs):
        if self.type == "human":
            return self.get_human_move(inputs)

        if self.type == "random":
            return self.get_random_move()

    def get_random_move():
        return

    def get_human_move(self, inputs):
        delta = [0, 0]  # [x, y]

        print(inputs)
        if inputs["up"]:
            delta[1] -= 5

        if inputs["down"]:
            delta[1] += 5

        if inputs["left"]:
            delta[0] -= 5

        if inputs["right"]:
            delta[0] += 5

        print(delta)
        if delta[0] != 0 and delta[1] != 0:
            print([delta[0] / self.root2, delta[1] / self.root2])
            delta = [delta[0] / self.root2, delta[1] / self.root2]

        print(delta)

        return delta
