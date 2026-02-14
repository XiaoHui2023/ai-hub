from pathlib import Path
from core import set_log, load_configs
from config import Config
from api import App
import argparse
import time

DEFAULT_FILE = str(Path(__file__).parent / "default.yaml")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="input", type=str, help="input json or yaml file")
    return parser.parse_args()


def main(input_file: str):
    metadata = load_configs(DEFAULT_FILE, input_file)
    cfg = Config(**metadata)
    set_log(cfg.log)
    app = App(cfg)
    app.start()

    try:
        while app.is_running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        app.stop()


if __name__ == "__main__":
    args = get_args()
    main(args.input)
