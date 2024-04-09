import multiprocessing as mp
from main import Main
import json
import os


SIM_AMOUNT = 8
CPU_CORES = 8
MAX_TICKS = 1_000

RESULTS_FOLDER = "Results/"


def get_new_folder():
    return f"batchrun_{max([int(x.split('.')[0].split('_')[-1]) for x in [x for x in os.listdir(RESULTS_FOLDER) if not x.endswith('.gitkeep')]] + [0]) + 1}"


def get_json_path(folder, id):
    return RESULTS_FOLDER + f"{folder}/" + f"SIM_{id}"


def run_main(inputs):
    id, folder = inputs

    print("starting sim:", id)
    mp.freeze_support()

    m = Main(headless=True, self_restart=False, max_ticks=MAX_TICKS, prints=False)
    m.start()
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
