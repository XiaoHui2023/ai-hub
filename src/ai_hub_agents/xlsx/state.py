"""XlsxAgent 自定义状态定义。"""

from __future__ import annotations

from langchain.agents import AgentState


class XlsxState(AgentState):
    """XlsxAgent 的结构化状态。

    继承 AgentState（messages + structured_response），
    新增 input_file / output_file 通过 invoke() 传入，
    工具通过 InjectedState 自动获取，LLM 无需感知。
    """

    input_file: str
    output_file: str
