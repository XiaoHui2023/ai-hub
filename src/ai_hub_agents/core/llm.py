"""轻量 LLM 工厂 — 供路由/摘要/搜索等辅助任务使用。

优先读取 LITE_* 环境变量，未配置则降级复用主模型。
"""

from __future__ import annotations

import logging
import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def _model_tag(llm: BaseChatModel) -> str:
    """从 LLM 实例提取模型名标识。"""
    if hasattr(llm, "model_name"):
        return llm.model_name
    if hasattr(llm, "model"):
        return str(llm.model)
    return type(llm).__name__


def create_lite_llm() -> BaseChatModel | None:
    """尝试创建轻量 LLM 实例，配置不完整时返回 None。

    环境变量优先级：LITE_* > 主模型（API_KEY / API_BASE_URL / MODEL_NAME）。
    """
    api_key = os.environ.get("LITE_API_KEY") or os.environ.get("API_KEY")
    base_url = os.environ.get("LITE_API_BASE_URL") or os.environ.get("API_BASE_URL")
    model = os.environ.get("LITE_MODEL_NAME") or os.environ.get("MODEL_NAME")

    if not all([api_key, base_url, model]):
        return None

    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0,
        streaming=False,
    )
    logger.info("[LLM] 轻量模型就绪: %s", model)
    return llm


def resolve_lite_llm(llm: BaseChatModel) -> BaseChatModel:
    """获取辅助任务用的 LLM：优先轻量模型，不可用时降级为主模型。"""
    lite = create_lite_llm()
    if lite is not None:
        return lite
    logger.debug("[LLM] 未配置轻量 LLM，降级使用主模型: %s", _model_tag(llm))
    return llm
