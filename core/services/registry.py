from typing import Dict, Tuple, Type
from core.services.base_operation import BaseOperation

_registry: Dict[Tuple[str, str], Type[BaseOperation]] = {}

def register(service: str, provider: str):
    """装饰器：注册一个实现类"""
    def decorator(cls: Type[BaseOperation]) -> Type[BaseOperation]:
        _registry[(service, provider)] = cls
        return cls
    return decorator

def get(service: str, provider: str) -> Type[BaseOperation]:
    key = (service, provider)
    if key not in _registry:
        raise KeyError(f"未找到实现: service='{service}', provider='{provider}'")
    return _registry[key]