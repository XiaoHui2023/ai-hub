"""search_urls 节点测试。"""

from __future__ import annotations

from langchain_core.messages import HumanMessage

from ai_hub_agents.search.nodes.search_urls import make_search_urls
from ai_hub_agents.search.providers.base import SearchResult

from .conftest import MockSearchProvider


class TestSearchUrlsNode:

    def test_extracts_query_from_message(self, mock_provider):
        node = make_search_urls(mock_provider)
        state = {"messages": [HumanMessage(content="LangGraph 是什么")]}
        result = node(state)
        assert result["search_query"] == "LangGraph 是什么"

    def test_max_results_truncation(self):
        provider = MockSearchProvider([
            SearchResult(url=f"https://example.com/{i}", title=f"R{i}")
            for i in range(10)
        ])
        node = make_search_urls(provider, max_results=3)
        state = {"messages": [HumanMessage(content="test")]}
        result = node(state)
        assert len(result["search_results"]) == 3

    def test_empty_results(self, mock_provider_empty):
        node = make_search_urls(mock_provider_empty)
        state = {"messages": [HumanMessage(content="test")]}
        result = node(state)
        assert result["search_results"] == []

    def test_return_fields_complete(self, mock_provider):
        node = make_search_urls(mock_provider)
        state = {"messages": [HumanMessage(content="hello")]}
        result = node(state)
        assert "search_query" in result
        assert "search_results" in result
        assert isinstance(result["search_results"], list)
        for item in result["search_results"]:
            assert "url" in item
            assert "title" in item
