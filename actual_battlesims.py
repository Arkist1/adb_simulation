from itertools import combinations_with_replacement
import utils
from entities import Agent, Enemy
import numpy as np

import matplotlib.pyplot as plt

import os.path as pt

battles = []

agent_types = [
    "cheater",
    "helper",
    "copycat",
    "copykitten",
    "simpleton",
    "random",
    "grudger",
    "detective",
]
plt_dir = "Test_plots/"

test_types = ["helper", "cheater"]


# battles.extend(combinations_with_replacement(agent_types, 2))
battles = [test_types]

print(len(battles))

enemy_hp = 400
N_sims = 1000
agent_hp = 100


all_res = {agent: [] for agent in test_types}

for enemy_hp in range(25, 401, 25):

    battle_results = {agent: [] for agent in test_types}
    for _ in range(N_sims):
        for type1, type2 in battles:
            a1 = Agent(None, battle_type=type1, health=agent_hp)
            a2 = Agent(None, battle_type=type2, health=agent_hp)

            e = Enemy(None, health=enemy_hp)
            utils.Battle([a1, a2], [e]).run_battle()

            for agent in [a1, a2]:
                battle_results[agent.battle_type].append(agent.health)

    # print(battle_results)

    results = {agent: sum(hp) / len(hp) for agent, hp in battle_results.items()}

    for agent in all_res:
        all_res[agent].append(results[agent])

    sorted_res = dict(sorted(results.items(), key=lambda x: x[1], reverse=False))

    plt.barh(list(sorted_res.keys()), list(sorted_res.values()))
    plt.title(f"{agent_hp=}, {enemy_hp=}, {N_sims=}")
    plt.xlim(0, agent_hp)

    plt.ylabel("Agent type")
    plt.xlabel("HP")
    plt.savefig(pt.join(plt_dir, f"RUN_{enemy_hp=}.png"), dpi=450)
    plt.clf()  # clear fig


# print(list(all_res.values()))
# print(np.transpose(all_res.values()))
plt.plot(np.transpose(list(all_res.values())))
plt.legend(all_res.keys())
plt.title("Helper en Cheater")
plt.xlabel("Enemy hp")
plt.ylabel("Agent hp")
plt.savefig(plt_dir, dpi=450)
