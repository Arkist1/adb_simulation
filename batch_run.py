import multiprocessing as mp
from main import Main

mp.freeze_support()

SIM_AMOUNT = 1
CPU_CORES = 8
MAX_TICKS = 1000

RESULTS_FOLDER = "Results/"


def get_json_path():
    return RESULTS_FOLDER + f"SIM_{hash()}"


def run_main():
    m = Main(headless=True, self_restart=False, max_ticks=MAX_TICKS)
    m.start()
    # m.save_results(get_json_path())


with mp.Pool(CPU_CORES) as p:
    p.map(run_main, range(SIM_AMOUNT))
