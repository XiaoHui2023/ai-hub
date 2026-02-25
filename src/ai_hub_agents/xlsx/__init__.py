from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from ai_hub.core import BaseAgent

from .tools import (
    execute_python,
    pack_office,
    read_excel,
    recalc_formulas,
    unpack_office,
    validate_office,
)


class XlsxAgent(BaseAgent):
    """Excel 电子表格处理 Agent。

    支持读取、创建、编辑 Excel 文件，公式计算，格式化，
    以及 Office 文件（DOCX/PPTX/XLSX）的 XML 级别编辑。
    """

    name = "xlsx"
    description = (
        "处理 Excel 电子表格文件（.xlsx/.xlsm/.csv/.tsv）的专业 Agent，"
        "支持读取、创建、编辑、公式计算和格式化。"
    )

    @classmethod
    def get_tools(cls, **kwargs: Any) -> list[BaseTool]:
        return [
            read_excel,
            execute_python,
            recalc_formulas,
            unpack_office,
            pack_office,
            validate_office,
        ]

    @classmethod
    def create(cls, llm: BaseChatModel, **kwargs: Any) -> XlsxAgent:
        tools = cls.get_tools(**kwargs)
        prompt = cls.get_prompt()
        graph = create_agent(llm, tools, system_prompt=prompt)
        return cls(graph)
