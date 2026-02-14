_registry = {}

def register(provider: str, service: str):
    '''装饰器，注册对接类'''
    def decorator(cls):
        _registry[(provider, service)] = cls
        return cls
    return decorator

def get_handler(provider: str, service: str):
    key = (provider, service)
    if key not in _registry:
        raise ValueError(f"不支持: {provider}/{service}")
    return _registry[key]