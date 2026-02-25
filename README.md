# AI Hub

模块化 AI Agent 框架，基于 LangChain / LangGraph。

每个 Agent 都可以独立运行，也可以作为 **工具** 或 **节点** 嵌入更大的工作流。

## 安装

```bash
pip install ai-hub-agents
```

## 项目结构

```
ai_hub/
├── pyproject.toml
├── README.md
└── src/
    └── ai_hub_agents/
        ├── __init__.py
        ├── core/                   # 公共基础
        │   ├── __init__.py
        │   └── base_agent.py       # BaseAgent 抽象基类
        ├── excel/                  # (示例) Excel Agent
        │   ├── __init__.py
        │   ├── agent.py
        │   ├── prompt.md
        │   └── tools/
        └── search/                 # (示例) 搜索 Agent
            └── ...
```

## 快速开始

### 1. 创建子 Agent

继承 `BaseAgent`，实现 `get_tools()` 和 `create()`：

```python
from ai_hub.core import BaseAgent
from langgraph.prebuilt import create_react_agent

class ExcelAgent(BaseAgent):
    name = "excel"
    description = "Excel 文件操作专家"

    @classmethod
    def get_tools(cls, **kwargs):
        return [read_sheet, write_sheet]

    @classmethod
    def create(cls, llm, **kwargs):
        tools = cls.get_tools()
        prompt = cls.get_prompt()       # 自动读取同目录 prompt.md
        graph = create_react_agent(llm, tools, prompt=prompt)
        return cls(graph)
```

### 2. 作为工具调用

将子 Agent 包装为 Tool，交给父 Agent 使用：

```python
excel_tool = ExcelAgent.as_tool(llm)
search_tool = SearchAgent.as_tool(llm)

supervisor = create_react_agent(llm, [excel_tool, search_tool])
supervisor.invoke({"messages": [("human", "汇总 data.xlsx 并搜索相关资料")]})
```

### 3. 作为节点组成工作流

将子 Agent 包装为节点，用 LangGraph 编排流程：

```python
from langgraph.graph import StateGraph, MessagesState

builder = StateGraph(MessagesState)
builder.add_node("search", SearchAgent.as_node(llm))
builder.add_node("excel", ExcelAgent.as_node(llm))
builder.add_edge("search", "excel")
builder.set_entry_point("search")
builder.set_finish_point("excel")

workflow = builder.compile()
workflow.invoke({"messages": [("human", "搜索数据并写入表格")]})
```

### 4. 直接执行

```python
agent = ExcelAgent.create(llm)
result = agent.invoke("读取 data.xlsx 的第一个 sheet")

# 流式输出
for mode, event in agent.stream("汇总所有数据"):
    print(mode, event)
```
