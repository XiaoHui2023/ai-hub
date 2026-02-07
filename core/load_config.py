from omegaconf import OmegaConf
import json

def load_config(config_file:str) -> dict:
    '''加载配置文件'''
    if config_file.endswith(".json"):
        return load_json(config_file)
    elif config_file.endswith(".yaml"):
        return load_yaml(config_file)
    else:
        raise ValueError(f"不支持的文件格式: {config_file}")

def load_json(config_file:str) -> dict:
    '''加载json文件'''
    with open(config_file, "r") as f:
        data = json.load(f)
    return data

def load_yaml(config_file:str) -> dict:
    '''加载yaml文件'''
    with open(config_file, "r") as f:
        data = OmegaConf.load(f)
    return OmegaConf.to_container(data)