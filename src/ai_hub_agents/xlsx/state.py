"""XlsxAgent 自定义状态定义。"""

from typing import Annotated

from langchain.agents import AgentState

from ai_hub_agents.core import InputFile, OutputFile


class XlsxState(AgentState):
    """XlsxAgent 的结构化状态。

    继承 AgentState（messages + structured_response），
    新增 input_file / output_file 通过 invoke() 传入，
    工具通过 InjectedState 自动获取，LLM 无需感知。
    """

    input_file: Annotated[str, InputFile()]
    output_file: Annotated[str, OutputFile(ext=".xlsx")]
