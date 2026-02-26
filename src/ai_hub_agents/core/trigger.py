from __future__ import annotations

import logging
from typing import Callable

from .event import Event, EventBus

logger = logging.getLogger(__name__)


class Trigger:
    """触发器：订阅事件 → 判断条件 → 执行动作。

    Args:
        event: 要订阅的事件名称（如 "run_complete", "node_complete"）。
        action: 条件满足时执行的动作，接收 Event 参数。
        condition: 可选的过滤条件，返回 True 时才执行 action。
                   省略则无条件触发（只要事件名匹配）。
        name: 触发器名称，用于日志。
    """

    def __init__(
        self,
        event: str,
        action: Callable[[Event], None],
        condition: Callable[[Event], bool] | None = None,
        name: str = "",
    ) -> None:
        self.event = event
        self.action = action
        self.condition = condition
        self.name = name or f"trigger:{event}"

    def __call__(self, e: Event) -> None:
        if e.name != self.event:
            return
        if self.condition is not None and not self.condition(e):
            return
        logger.debug("[%s] 触发", self.name)
        self.action(e)

    def register(self, bus: EventBus) -> None:
        bus.subscribe(self)
