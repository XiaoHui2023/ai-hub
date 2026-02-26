"""SearchAgent 测试公共 fixture。"""

from __future__ import annotations

import pytest

from ai_hub_agents.search.providers.base import SearchProvider, SearchResult
from ai_hub_agents.test import ColorStreamRenderer, load_test_llm, setup_logging


def pytest_configure(config):
    setup_logging()


class MockSearchProvider(SearchProvider):
    """可控返回值的 Mock Provider。"""

    name = "mock"

    def __init__(self, results: list[SearchResult] | None = None) -> None:
        self._results = results or []

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        return self._results[:max_results]

    @classmethod
    def is_available(cls) -> bool:
        return True


@pytest.fixture(scope="session")
def llm():
    return load_test_llm()


@pytest.fixture()
def mock_provider():
    return MockSearchProvider([
        SearchResult(url="https://example.com/1", title="Result 1"),
        SearchResult(url="https://example.com/2", title="Result 2"),
        SearchResult(url="https://example.com/3", title="Result 3"),
    ])


@pytest.fixture()
def mock_provider_empty():
    return MockSearchProvider([])


@pytest.fixture(scope="session")
def agent(llm):
    """整个测试会话复用同一个 agent 实例（集成测试用）。"""
    from ai_hub_agents.search import SearchAgent

    return SearchAgent.create(llm)


@pytest.fixture()
def renderer():
    return ColorStreamRenderer()
