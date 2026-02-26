"""summarize 节点测试。"""

from __future__ import annotations

from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ai_hub_agents.search.nodes.summarize import _load_prompt, make_summarize


class TestLoadPrompt:

    def test_prompt_loads_and_contains_keywords(self):
        prompt = _load_prompt()
        assert len(prompt) > 0
        assert any(kw in prompt for kw in ["Markdown", "总结", "提炼", "关键"])


class TestSummarizeNode:

    def test_empty_content_fallback(self):
        mock_llm = MagicMock()
        node = make_summarize(mock_llm)
        result = node({"search_fetched": [], "search_query": "test"})
        assert result["search_summary"] == ""
        mock_llm.invoke.assert_not_called()

    def test_llm_invoke_params(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="总结内容")
        node = make_summarize(mock_llm)
        state = {
            "search_fetched": [
                {"url": "https://a.com", "markdown": "内容A"},
            ],
            "search_query": "测试问题",
        }
        result = node(state)
        args = mock_llm.invoke.call_args[0][0]
        assert isinstance(args[0], SystemMessage)
        assert isinstance(args[1], HumanMessage)
        assert "测试问题" in args[1].content
        assert result["search_summary"] == "总结内容"

    def test_multi_source_merge(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="合并总结")
        node = make_summarize(mock_llm)
        state = {
            "search_fetched": [
                {"url": "https://a.com", "markdown": "内容A"},
                {"url": "https://b.com", "markdown": "内容B"},
            ],
            "search_query": "问题",
        }
        result = node(state)
        content = mock_llm.invoke.call_args[0][0][1].content
        assert "https://a.com" in content
        assert "https://b.com" in content
        assert result["search_summary"] == "合并总结"
