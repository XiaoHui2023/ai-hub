"""场景：混合对话 — 验证 QaAgent 在闲聊和搜索间正确切换。"""

from __future__ import annotations

import pytest

from ai_hub_agents.qa import QaAgent


@pytest.fixture()
def qa_agent(llm):
    return QaAgent.create(llm)


class TestMixedConversation:

    def test_chat_then_search(self, qa_agent, renderer):
        """先闲聊再搜索，能正确切换路径。"""
        r1 = qa_agent.invoke("你好呀")
        assert isinstance(r1, str)
        assert len(r1) > 2

        r2 = qa_agent.invoke("RAG 技术是什么？帮我搜索一下")
        assert isinstance(r2, str)
        assert any(kw in r2 for kw in ["RAG", "检索", "生成", "Retrieval"])

    def test_search_then_followup(self, qa_agent, renderer):
        """搜索后追问。"""
        qa_agent.invoke("RAG 是什么技术？")
        result = qa_agent.invoke("它有哪些典型应用场景？")
        assert isinstance(result, str)
        assert len(result) > 20
