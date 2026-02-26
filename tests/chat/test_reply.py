"""reply 节点单元测试。"""

from __future__ import annotations

from unittest.mock import MagicMock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ai_hub_agents.chat.nodes.reply import make_reply


class TestReplyNode:

    def _make_state(self, messages=None, recalled="", context=""):
        return {
            "messages": messages or [HumanMessage(content="你好")],
            "chat_recalled": recalled,
            "chat_context": context,
        }

    def test_basic_reply(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="你好！")
        node = make_reply(mock_llm, "你是助手")
        result = node(self._make_state())
        assert result["messages"][0].content == "你好！"

    def test_prompt_as_system_message(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="回复")
        node = make_reply(mock_llm, "我是系统提示")
        node(self._make_state())
        args = mock_llm.invoke.call_args[0][0]
        assert isinstance(args[0], SystemMessage)
        assert args[0].content == "我是系统提示"

    def test_recalled_appended_to_prompt(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="回复")
        node = make_reply(mock_llm, "提示")
        node(self._make_state(recalled="用户喜欢蓝色"))
        args = mock_llm.invoke.call_args[0][0]
        assert "用户喜欢蓝色" in args[0].content

    def test_context_appended_to_prompt(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="回复")
        node = make_reply(mock_llm, "提示")
        node(self._make_state(context="搜索摘要内容"))
        args = mock_llm.invoke.call_args[0][0]
        assert "搜索摘要内容" in args[0].content

    def test_both_recalled_and_context(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="回复")
        node = make_reply(mock_llm, "提示")
        node(self._make_state(recalled="记忆片段", context="搜索摘要"))
        args = mock_llm.invoke.call_args[0][0]
        assert "记忆片段" in args[0].content
        assert "搜索摘要" in args[0].content

    def test_empty_recalled_not_appended(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="回复")
        node = make_reply(mock_llm, "原始提示")
        node(self._make_state(recalled=""))
        args = mock_llm.invoke.call_args[0][0]
        assert "你记得" not in args[0].content

    def test_multi_turn_messages_passed(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="回复")
        node = make_reply(mock_llm, "提示")
        messages = [
            HumanMessage(content="第一轮"),
            AIMessage(content="回复一"),
            HumanMessage(content="第二轮"),
        ]
        node(self._make_state(messages=messages))
        args = mock_llm.invoke.call_args[0][0]
        assert len(args) == 4  # 1 SystemMessage + 3 chat messages
        assert args[1].content == "第一轮"
        assert args[2].content == "回复一"
        assert args[3].content == "第二轮"
