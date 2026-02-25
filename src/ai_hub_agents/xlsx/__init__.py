from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from langgraph.graph import END, START, StateGraph

from ai_hub_agents.core import BaseAgent

from .nodes import auto_init_output
from .state import XlsxState
from .tools import ALL_TOOLS


class XlsxAgent(BaseAgent):
    """Excel 电子表格处理 Agent。

    支持读取、创建、编辑 Excel 文件，公式计算，格式化，
    以及 Office 文件（DOCX/PPTX/XLSX）的 XML 级别编辑。

    输入/输出文件通过 State 传递，工具通过 InjectedState 自动获取路径。
    输出文件在 agent 执行前自动初始化（从输入复制或创建空工作簿）。
    """

    name = "xlsx"
    description = (
        "处理 Excel 电子表格文件（.xlsx/.xlsm/.csv/.tsv）的专业 Agent，"
        "支持读取、创建、编辑、公式计算和格式化。"
    )
    state_schema = XlsxState

    @classmethod
    def get_tools(cls, **kwargs: Any) -> list[BaseTool]:
        return list(ALL_TOOLS)

    @classmethod
    def create(cls, llm: BaseChatModel, **kwargs: Any) -> XlsxAgent:
        tools = cls.get_tools(**kwargs)
        prompt = cls.get_prompt()
        agent_graph = create_agent(
            llm,
            tools,
            system_prompt=prompt,
            state_schema=cls.state_schema,
        )

        builder = StateGraph(cls.state_schema)
        builder.add_node("init", auto_init_output)
        builder.add_node("agent", agent_graph)
        builder.add_edge(START, "init")
        builder.add_edge("init", "agent")
        builder.add_edge("agent", END)
        graph = builder.compile()

        return cls(graph)
