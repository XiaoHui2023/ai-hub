from core import set_log,load_config
from config import Config
from api import App
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="input", type=str, help="input json or yaml file")
    return parser.parse_args()

def main(input_file:str):
    '''
    主函数
    input_file: 输入文件
    '''
    metadata = load_config(input_file)
    cfg = Config(**metadata)
    set_log(cfg.log)
    app = App(cfg)
    app.run()

if __name__ == "__main__":
    args = get_args()
    main(args.input)