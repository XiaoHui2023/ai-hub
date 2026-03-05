from ai_hub_agents.callback import Callback

class A(Callback):
    callback_name: str = "A"
    """回调名称"""
    name: str
    """名称"""

class Other:
    def __init__(self):
        @A
        def _(cb:A):
            print(f"on_{cb.callback_name}: {cb.name}")


if __name__ == "__main__":
    Other()
    A(name="test")