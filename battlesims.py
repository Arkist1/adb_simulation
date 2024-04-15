# from itertools import combinations_with_replacement
from itertools import combinations
import multiprocessing as mp
from main import Main
from utils import Globals
from entities import Agent, Enemy
import json
import os
import pygame
import dotenv

dotenv.load_dotenv()

# battles = list(combinations_with_replacement(["copycat", "cheater", "helper", "grudger", "detective"], 2) )
battles = []
for r in range(2, 6):
    battles.extend(
        combinations(["copycat", "cheater", "helper", "grudger", "detective"], r)
    )

print(battles)
SIM_AMOUNT = len(battles)
CPU_CORES = 4
MAX_TICKS = 1000

RUN_HEADLESS = False

RESULTS_FOLDER = "Results/"


def get_new_folder():
    return f"batchrun_{max([int(x.split('.')[0].split('_')[-1]) for x in [x for x in os.listdir(RESULTS_FOLDER) if not x.endswith('.gitkeep')]] + [0]) + 1}"


def get_json_path(folder, id):
    return RESULTS_FOLDER + f"{folder}/" + f"SIM_{id}.json"


def run_main(inputs):
    id, folder = inputs

    t0, t1 = battles[id]
    print(f"starting sim: {id=}, {t0=}, {t1=}")
    mp.freeze_support()

    m = Main(
        headless=RUN_HEADLESS, self_restart=False, max_ticks=MAX_TICKS, prints=False
    )

    x0 = Globals.TILE_WIDTH / 3
    x1 = Globals.TILE_WIDTH / 3 * 2
    y0 = Globals.TILE_HEIGHT / 3
    y1 = Globals.TILE_HEIGHT / 3 * 2

    m.single_init()

    for p in list(m.tile_manager.players):
        m.tile_manager.remove_entity(p)

    for p in list(m.tile_manager.enemies):
        m.tile_manager.remove_entity(p)

    p0 = Agent(m.screen, start_pos=pygame.Vector2(x0, y0), battle_type=t0)
    p1 = Agent(m.screen, start_pos=pygame.Vector2(x1, y0), battle_type=t1)
    e0 = Enemy(m.screen, control_type="enemy", start_pos=pygame.Vector2(x0, y1))
    e1 = Enemy(m.screen, control_type="enemy", start_pos=pygame.Vector2(x1, y1))
    m.tile_manager.add_entity(p0)
    m.tile_manager.add_entity(p1)
    m.tile_manager.add_entity(e0)
    m.tile_manager.add_entity(e1)

    m.single_start()
    m.save_logs(get_json_path(folder, id))


if __name__ == "__main__":
    folder = get_new_folder()

    os.makedirs(RESULTS_FOLDER + folder)

    CONFIG = {
        "RUN_AMOUNT": SIM_AMOUNT,
        "CORE_AMOUNT": CPU_CORES,
        "MAX_TICKS": MAX_TICKS,
    }
    json.dump(CONFIG, open(RESULTS_FOLDER + f"{folder}/" + "config.json", "w"))

    with mp.Pool(CPU_CORES) as p:
        p.map(run_main, zip(range(SIM_AMOUNT), [folder] * SIM_AMOUNT))
