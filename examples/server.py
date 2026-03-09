import argparse
from ai_hub_agents import setup_log,load_settings,run
from ai_hub_agents.renderers import EventMonitor

def get_args() -> argparse.Namespace:
    """获取命令行参数"""
    parser = argparse.ArgumentParser(description='AI Hub Agents')
    parser.add_argument('input_yaml', type=str, nargs='?', help='输入YAML配置文件')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    load_settings(args.input_yaml)
    setup_log()
    EventMonitor()
    run()