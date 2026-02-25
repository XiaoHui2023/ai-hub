"""终端彩色流式渲染器。

作为 StreamCallback 的一种实现，将 Agent 的 stream 事件
以彩色 ANSI 格式通过 logging 输出。可作为模板编写其他渲染器
（如 Rich、JSON、WebSocket 等）。
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import AIMessage

from ai_hub_agents.core.callbacks import StreamCallback

logger = logging.getLogger("ai_hub_agents.stream")

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


class ColorStreamRenderer(StreamCallback):
    """终端彩色流式渲染器，通过 logging.info 输出。"""

    def on_stream_start(self) -> None:
        logger.info(f"{DIM}{'─' * 50}{RESET}")

    def on_stream_end(self, result: str) -> None:
        logger.info(f"{DIM}{'─' * 50}{RESET}")

    def on_ai_message(self, message: AIMessage) -> None:
        text = message.content[:200]
        logger.info(f"{CYAN}🤖 AI{RESET}  {text}")

    def on_tool_call(self, name: str, args: dict[str, Any]) -> None:
        logger.info(
            f"{YELLOW}🔧 Call{RESET}  "
            f"{BOLD}{name}{RESET} "
            f"{DIM}{args}{RESET}"
        )

    def on_tool_result(self, name: str, content: str) -> None:
        logger.info(
            f"{GREEN}✅ Result{RESET}  "
            f"{BOLD}{name}{RESET}: "
            f"{DIM}{content[:300]}{RESET}"
        )

    def on_tool_error(self, name: str, content: str) -> None:
        logger.info(
            f"{RED}❌ Error{RESET}  "
            f"{BOLD}{name}{RESET}: "
            f"{DIM}{content[:300]}{RESET}"
        )
