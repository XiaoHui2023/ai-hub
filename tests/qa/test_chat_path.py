"""场景：闲聊路径 — 验证 QaAgent 对不需要搜索的问题直接回答。"""

from __future__ import annotations


class TestChatPath:

    def test_greeting_no_search(self, agent, renderer):
        """打招呼不触发搜索，直接回答。"""
        result = agent.invoke("你好，今天心情怎么样？", callbacks=[renderer])
        assert isinstance(result, str)
        assert len(result) > 2

    def test_opinion_direct_answer(self, agent, renderer):
        """观点类问题直接回答，不需要搜索。"""
        result = agent.invoke(
            "你觉得学编程应该从哪门语言入手？", callbacks=[renderer]
        )
        assert isinstance(result, str)
        assert len(result) > 10

    def test_simple_math(self, agent, renderer):
        """简单计算题直接回答。"""
        result = agent.invoke("123 乘以 456 等于多少？", callbacks=[renderer])
        assert "56088" in result
