"""LLM 响应后处理。

统一处理各模型返回内容中的特殊标记，如 <think> 思考块等。
"""

from __future__ import annotations

import re

_THINK_PATTERN = re.compile(r"<think>.*?</think>\s*", flags=re.DOTALL)


def strip_thinking(text: str) -> str:
    """移除模型输出中的 <think>...</think> 思考块。

    兼容 Qwen、DeepSeek 等支持思考模式的模型。
    """
    return _THINK_PATTERN.sub("", text).lstrip()


def clean_response(text: str) -> str:
    """对 LLM 最终响应做全部后处理。

    当前包含:
      - strip_thinking: 移除 <think> 块

    后续可在此扩展更多处理步骤。
    """
    return strip_thinking(text)
