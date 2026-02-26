"""LangGraph Studio 入口 — 自动发现所有 Agent。

启动: langgraph dev
需要 .env 文件配置: API_KEY, API_BASE_URL, MODEL_NAME

新增 Agent 子包后，只需在 langgraph.json 中添加一行引用即可。
变量命名规则: {agent.name}_graph （如 xlsx_graph）
"""

import importlib
import os
import pkgutil

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

import ai_hub_agents
from ai_hub_agents.core import BaseAgent

load_dotenv()

llm = ChatOpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ["API_BASE_URL"],
    model=os.environ["MODEL_NAME"],
    temperature=0,
)


for _, module_name, is_pkg in pkgutil.iter_modules(ai_hub_agents.__path__):
    if is_pkg and module_name != "core":
        importlib.import_module(f"ai_hub_agents.{module_name}")

for _cls in BaseAgent.__subclasses__():
    _agent = _cls.create(llm, platform_mode=True)
    globals()[f"{_cls.name}_graph"] = _agent._graph
