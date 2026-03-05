import argparse
from .core import setup_log
from .config import Config
from .core.agent import Agent

def get_args() -> argparse.Namespace:
    """获取命令行参数"""
    parser = argparse.ArgumentParser(description='AI Hub Agents')
    parser.add_argument('input_yaml', type=str, nargs='?', help='输入YAML配置文件 (默认: config.yaml)')
    args = parser.parse_args()
    return args

def main(input_yaml:str|None):
    """主函数"""
    if input_yaml:
        with open(input_yaml) as f:
            config = Config.model_validate_json(f.read())
    else:
        config = Config()
    setup_log(config.log_dir, config.log_level)
    agent = Agent(config)
    agent.run(config)