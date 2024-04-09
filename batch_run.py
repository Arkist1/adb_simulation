import multiprocessing as mp
from main import Main

SIM_AMOUNT = 8
CPU_CORES = 8
MAX_TICKS = 30_000

RESULTS_FOLDER = "Results/"


def get_json_path():
    return RESULTS_FOLDER + f"SIM_{hash()}"


def run_main(id=None):
    print("starting sim:", id)
    mp.freeze_support()

    m = Main(headless=False, self_restart=False, max_ticks=MAX_TICKS)
    m.start()
    # m.save_results(get_json_path())


if __name__ == "__main__":
    with mp.Pool(CPU_CORES) as p:
        p.map(run_main, range(SIM_AMOUNT))
