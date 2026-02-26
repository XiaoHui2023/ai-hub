from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class RunContext:
    """一次 run 的公共上下文，由框架构建，事件携带，触发器透传。"""

    thread_id: str | None = None
    config: dict | None = None
    state: dict = field(default_factory=dict)


@dataclass
class Event:
    """事件基类。所有事件都携带 RunContext。"""

    ctx: RunContext
    name: str


@dataclass
class RunStartEvent(Event):
    """graph 执行开始。"""

    name: str = "run_start"


@dataclass
class NodeCompleteEvent(Event):
    """某个节点执行完成。"""

    name: str = "node_complete"
    node: str = ""
    update: dict = field(default_factory=dict)


@dataclass
class RunCompleteEvent(Event):
    """graph 整体执行完成。此时 ctx.state 为完整最终状态。"""

    name: str = "run_complete"


@dataclass
class RunErrorEvent(Event):
    """graph 执行异常。"""

    name: str = "run_error"
    exception: Exception | None = None


class EventBus:
    """事件广播总线。只负责发射和分发，不关心监听者的逻辑。"""

    def __init__(self) -> None:
        self._listeners: list[Callable[[Event], None]] = []

    def subscribe(self, listener: Callable[[Event], None]) -> None:
        self._listeners.append(listener)

    def emit(self, event: Event) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                logger.exception("事件监听器执行失败: %s", event.name)
