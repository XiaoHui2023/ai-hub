"""搜索 Provider 基类 — 定义统一的搜索接口和结果结构。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    """单条搜索结果，仅含 URL 和元信息，不含内容。"""

    url: str
    title: str
    published_date: str | None = None


class SearchProvider(ABC):
    """搜索引擎 Provider 抽象基类。

    子类需实现 name、search()、is_available()。
    """

    name: str

    @abstractmethod
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """执行搜索，返回 URL 列表。"""
        ...

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """检查当前环境是否可用（环境变量 / SDK 是否就绪）。"""
        ...
