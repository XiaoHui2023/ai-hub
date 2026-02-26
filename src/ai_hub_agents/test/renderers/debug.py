"""Debug 用 StreamCallback，记录每次 LLM 调用的完整输入/输出。"""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import AIMessage, BaseMessage

from ai_hub_agents.core.callbacks import StreamCallback


@dataclass
class LLMCheckpoint:
    """一次 LLM 调用的快照。"""

    input_messages: list[BaseMessage]
    output: AIMessage | None = None


class DebugStreamRenderer(StreamCallback):
    """测试用：记录所有 LLM 调用的完整输入/输出 checkpoint。

    使用方法::

        renderer = DebugStreamRenderer()
        result = agent.invoke("你好", callbacks=[renderer])
        print(renderer.dump())
        assert len(renderer.checkpoints) >= 1
    """

    def __init__(self) -> None:
        self.checkpoints: list[LLMCheckpoint] = []
        self._current: LLMCheckpoint | None = None

    def on_llm_start(self, messages: list[BaseMessage]) -> None:
        self._current = LLMCheckpoint(input_messages=list(messages))

    def on_llm_end(self, response: AIMessage) -> None:
        if self._current:
            self._current.output = response
            self.checkpoints.append(self._current)
            self._current = None

    def dump(self) -> str:
        """格式化输出所有 checkpoint，方便 debug。"""
        lines: list[str] = []
        for i, cp in enumerate(self.checkpoints):
            lines.append(f"=== LLM Call #{i + 1} ===")
            for msg in cp.input_messages:
                role = type(msg).__name__.replace("Message", "")
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                lines.append(f"  [{role}] {content[:200]}")
            if cp.output:
                content = cp.output.content if isinstance(cp.output.content, str) else str(cp.output.content)
                lines.append(f"  [AI Response] {content[:200]}")
                if cp.output.tool_calls:
                    for tc in cp.output.tool_calls:
                        lines.append(f"  [Tool Call] {tc['name']}({tc['args']})")
            lines.append("")
        return "\n".join(lines)
