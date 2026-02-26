"""场景：日常闲聊 — 验证 ChatAgent 的基础对话能力和 prompt 规则。"""

from __future__ import annotations


class TestGreeting:

    def test_hello_response(self, agent, renderer):
        """打招呼得到友好回复。"""
        result = agent.invoke("你好", callbacks=[renderer])
        assert isinstance(result, str)
        assert len(result) > 2

    def test_caring_question(self, agent, renderer):
        """关心类问题得到有温度的回复。"""
        result = agent.invoke("今天感觉好累啊", callbacks=[renderer])
        assert isinstance(result, str)
        assert len(result) > 5

    def test_no_emoji_in_response(self, agent, renderer):
        """遵守 prompt.md 规则，回复中不使用表情符号。"""
        result = agent.invoke("你好呀，跟我聊聊天吧", callbacks=[renderer])
        emoji_indicators = ["😀", "😊", "🤗", "👋", "🎉", "💪", "❤", "😄", "🙂"]
        for emoji in emoji_indicators:
            assert emoji not in result, f"回复中包含表情符号: {emoji}"
