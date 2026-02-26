"""终端彩色流式渲染器。

作为 StreamCallback 的一种实现，将 Agent 的 stream 事件
以彩色 ANSI 格式通过 logging 输出。可作为模板编写其他渲染器
（如 Rich、JSON、WebSocket 等）。
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

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

    def on_queue_wait(self, thread_id: str) -> None:
        logger.info(f"{YELLOW}⏳ 排队等待{RESET}  thread={DIM}{thread_id}{RESET}")

    def on_queue_resume(self, thread_id: str) -> None:
        logger.info(f"{GREEN}▶ 开始执行{RESET}  thread={DIM}{thread_id}{RESET}")

    def on_stream_start(self) -> None:
        logger.info(f"{DIM}{'─' * 50}{RESET}")

    def on_stream_end(self, result: str) -> None:
        logger.info(f"{DIM}{'─' * 50}{RESET}")

    def on_node(self, name: str) -> None:
        logger.info(f"{DIM}✅ Node 完成{RESET}  {BOLD}{name}{RESET}")

    def on_ai_message(self, message: AIMessage) -> None:
        text = message.content[:200]
        model = message.response_metadata.get("model_name", "") if message.response_metadata else ""
        label = f"{CYAN}🤖 AI{RESET}"
        if model:
            label += f" {DIM}({model}){RESET}"
        logger.info(f"{label}  {text}")

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

    def on_llm_start(self, messages: list[BaseMessage]) -> None:
        roles = [type(m).__name__.replace("Message", "") for m in messages]
        logger.info(
            f"{DIM}📨 LLM Start{RESET}  "
            f"{len(messages)} messages "
            f"{DIM}[{', '.join(roles)}]{RESET}"
        )

    def on_llm_end(self, response: AIMessage) -> None:
        preview = (response.content[:120] + "…") if len(response.content) > 120 else response.content
        has_tools = bool(response.tool_calls)
        label = f"{CYAN}📩 LLM End{RESET}"
        if has_tools:
            names = [tc["name"] for tc in response.tool_calls]
            label += f"  {DIM}tool_calls={names}{RESET}"
        else:
            label += f"  {DIM}{preview}{RESET}"
        logger.info(label)

    def on_background_submit(self, worker_name: str) -> None:
        logger.info(
            f"{DIM}🔄 Background{RESET}  "
            f"{BOLD}{worker_name}{RESET} 提交任务"
        )

    def on_background_done(self, worker_name: str, item_count: int) -> None:
        logger.info(
            f"{GREEN}✅ Background{RESET}  "
            f"{BOLD}{worker_name}{RESET} 完成 "
            f"{DIM}({item_count} 项){RESET}"
        )

    def on_background_error(self, worker_name: str, error: str, item_count: int) -> None:
        logger.info(
            f"{RED}❌ Background{RESET}  "
            f"{BOLD}{worker_name}{RESET} 失败: "
            f"{DIM}{error[:200]}{RESET}"
        )
