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

def load_configs(*config_files:str) -> dict:
    '''加载多个配置文件'''
    result = {}
    for config_file in config_files:
        result = deep_merge(result, load_config(config_file))
    return result

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

def deep_merge(base: dict, override: dict) -> dict:
    """深合并两个字典，只覆盖最底层的键"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result