"""router 节点单元测试。"""

from __future__ import annotations

from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ai_hub_agents.qa.nodes.router import make_router


class TestRouterNode:

    def _make_state(self, content="test"):
        return {"messages": [HumanMessage(content=content)]}

    def _make_mock_llm(self, response_text):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=response_text)
        return mock_llm

    def test_search_determination(self):
        node = make_router(self._make_mock_llm("SEARCH"))
        result = node(self._make_state("2026年AI新闻"))
        assert result["qa_needs_search"] is True

    def test_chat_determination(self):
        node = make_router(self._make_mock_llm("CHAT"))
        result = node(self._make_state("你好"))
        assert result["qa_needs_search"] is False

    def test_case_insensitive(self):
        node = make_router(self._make_mock_llm("search"))
        result = node(self._make_state("最新新闻"))
        assert result["qa_needs_search"] is True

    def test_extra_text_still_search(self):
        node = make_router(self._make_mock_llm("我认为需要 SEARCH 来回答"))
        result = node(self._make_state("最新技术"))
        assert result["qa_needs_search"] is True

    def test_irrelevant_reply_defaults_chat(self):
        node = make_router(self._make_mock_llm("我不确定该怎么分类"))
        result = node(self._make_state("随便聊聊"))
        assert result["qa_needs_search"] is False

    def test_message_structure(self):
        llm = self._make_mock_llm("CHAT")
        node = make_router(llm)
        node(self._make_state("测试消息"))
        args = llm.invoke.call_args[0][0]
        assert len(args) == 2
        assert isinstance(args[0], SystemMessage)
        assert isinstance(args[1], HumanMessage)
        assert args[1].content == "测试消息"
