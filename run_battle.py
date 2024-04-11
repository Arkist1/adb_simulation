from utils import Battle, BattleSummary
from entities import Agent, Enemy


agents = [Agent(None, health=100), Agent(None, health=200)]
enemies = [Enemy(None, health=300)]
b = Battle(agents, enemies)
print(BattleSummary(b))
b.one_round()
print(BattleSummary(b))

print()

agents = [Agent(None, health=100), Agent(None, health=200)]
enemies = [Enemy(None, health=300)]
b = Battle(agents, enemies)
print(BattleSummary(b))
b.run_battle()
print(BattleSummary(b))
