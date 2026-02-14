from typing import Dict, Optional, Tuple, Type
from core.services.base_operation import BaseOperation

_registry: Dict[Tuple[str, str, str, Optional[str]], Type[BaseOperation]] = {}

def register(service: str, operation: str, provider: str, model: Optional[str] = None):
    """装饰器：注册一个实现类，model 为 None 时作为该 provider 的默认实现"""
    def decorator(cls: Type[BaseOperation]) -> Type[BaseOperation]:
        _registry[(service, operation, provider, model)] = cls
        return cls
    return decorator

def get(service: str, operation: str, provider: str, model: Optional[str] = None) -> Type[BaseOperation]:
    """查找实现类，优先精确匹配 model，找不到则退回 provider 默认实现"""
    key = (service, operation, provider, model)
    if key in _registry:
        return _registry[key]
    # 退回到不指定 model 的默认实现
    fallback = (service, operation, provider, None)
    if fallback in _registry:
        return _registry[fallback]
    raise KeyError(
        f"未找到实现: service='{service}', operation='{operation}', "
        f"provider='{provider}', model='{model}'"
    )