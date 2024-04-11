from entities import Agent, Enemy


class Battle:
    def __init__(self, agents, enemies) -> None:
        self.agents = agents
        self.enemies = enemies
        self.history = {agent: [] for agent in self.agents}
        self.logs = []

    def run_battle(self):
        while (
            sum([enemy.health for enemy in self.enemies]) > 0
            and sum([player.health for player in self.agents]) > 0
        ):
            self.one_round()

    def one_round(self):
        active_agents = []

        for agent in self.agents:
            if agent.health > 0:
                if agent.do_battle(BattleSummary(self)):
                    self.history[agent].append(True)
                    active_agents.append(agent)
                else:
                    self.history[agent].append(False)

        self.battle_sim(active_agents)
        self.logs.append(BattleSummary(self).json())

    def battle_sim(self, active_agents):
        # get total damage
        total_enemy_damage = sum(
            [enemy.damage for enemy in self.enemies if enemy.health > 0]
        )
        total_player_damage = sum(
            [player.weapon.damage for player in active_agents if player.health > 0]
        )

        # distribute damage
        for agent in active_agents:
            agent.take_damage(int(total_enemy_damage / len(active_agents)))

        for enemy in self.enemies:
            enemy.take_damage(int(total_player_damage / len(self.enemies)))


class BattleSummary:
    def __init__(self, b: Battle) -> None:
        self.enemies = {enemy: enemy.health for enemy in b.enemies}
        self.agents = {agent: agent.health for agent in b.agents}
        self.agent_history = {
            agent: moves[-1] if len(moves) > 0 else None
            for agent, moves in b.history.items()
        }
        self.full_agent_history = b.history

    def __str__(self) -> str:
        return (
            f"Agent hp's: \t{self.agents.items()}, \n"
            + f"Enemy hp's: \t{self.enemies.items()} \n"
            + f"Battle  history: \t{self.agent_history}"
        )

    def json(self):
        return {
            "agents": {hash(agent): hp for agent, hp in self.agents.items()},
            "enemies": {hash(enemy): hp for enemy, hp in self.enemies.items()},
            "battle_history": {
                hash(agent): values for agent, values in self.full_agent_history.items()
            },
        }
