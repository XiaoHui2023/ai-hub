"""测试环境工具。

提供快速加载 .env 环境变量并创建 LLM 实例的公共函数，
避免每个测试脚本重复编写样板代码。
"""

from __future__ import annotations

import logging
import os
import signal
import sys
from typing import Any

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

_REQUIRED_KEYS = ("API_KEY", "API_BASE_URL", "MODEL_NAME")


def load_test_llm(**kwargs: Any) -> BaseChatModel:
    """从 .env 加载环境变量并创建 ChatOpenAI 实例。

    自动调用 load_dotenv()，检查必需的环境变量，
    返回可直接使用的 LLM 实例。kwargs 透传给 ChatOpenAI。
    """
    load_dotenv()
    missing = [k for k in _REQUIRED_KEYS if k not in os.environ]
    if missing:
        raise ValueError(f"缺少环境变量: {', '.join(missing)}，请在 .env 中配置")

    defaults: dict[str, Any] = dict(
        api_key=os.environ["API_KEY"],
        base_url=os.environ["API_BASE_URL"],
        model=os.environ["MODEL_NAME"],
        temperature=0,
        streaming=True,
    )
    defaults.update(kwargs)
    return ChatOpenAI(**defaults)


def setup_logging(level: int = logging.INFO) -> None:
    """配置日志，默认 INFO 级别以显示渲染器输出，同时抑制第三方库噪音。"""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    for name in ("httpx", "openai", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
