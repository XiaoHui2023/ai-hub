"""Provider 注册表 — 自动扫描、注册、解析可用 Provider。"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import SearchProvider

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, type[SearchProvider]] = {}


def register(cls: type[SearchProvider]) -> type[SearchProvider]:
    """装饰器：将 Provider 类注册到全局注册表。"""
    _REGISTRY[cls.name] = cls
    return cls


def _auto_scan() -> None:
    """自动扫描当前目录下所有模块，import 触发 @register。"""
    pkg_dir = Path(__file__).parent
    for info in pkgutil.iter_modules([str(pkg_dir)]):
        if info.name.startswith("_") or info.name == "base":
            continue
        try:
            importlib.import_module(f"{__package__}.{info.name}")
        except Exception:
            logger.debug("跳过 Provider 模块 %s（import 失败）", info.name)


def resolve_provider(name: str | None = None) -> "SearchProvider":
    """解析并实例化 Provider。

    Args:
        name: 显式指定 Provider 名称；None 则自动检测第一个可用的。

    Raises:
        ValueError: 找不到可用的 Provider。
    """
    _auto_scan()

    if name:
        if name not in _REGISTRY:
            raise ValueError(
                f"未知的搜索 Provider: {name!r}，"
                f"可用: {list(_REGISTRY.keys())}"
            )
        provider_cls = _REGISTRY[name]
        if not provider_cls.is_available():
            raise ValueError(f"Provider {name!r} 不可用（缺少环境变量或 SDK）")
        return provider_cls()

    for provider_cls in _REGISTRY.values():
        if provider_cls.is_available():
            logger.info("自动选择搜索 Provider: %s", provider_cls.name)
            return provider_cls()

    raise ValueError(
        "没有可用的搜索 Provider。请安装并配置至少一个 Provider "
        f"（已注册: {list(_REGISTRY.keys()) or '无'}）"
    )


def list_available() -> dict[str, bool]:
    """返回所有已注册 Provider 及其可用状态。"""
    _auto_scan()
    return {name: cls.is_available() for name, cls in _REGISTRY.items()}
