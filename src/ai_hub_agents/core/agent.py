from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from ai_hub_agents import settings
import json
from typing import List
from pathlib import Path
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from contextlib import AsyncExitStack
from ai_hub_agents.callback import LoadMCPTools,UserQuery,AssistantResponse,AgentCreate
from pydantic import BaseModel, ConfigDict
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from .json_store import JsonStore
import logging
from .message_simplify import messages_to_simple,simple_to_messages
from ai_hub_agents.tools import get_all_tools
from langgraph.graph.state import CompiledStateGraph

logger = logging.getLogger(__name__)

class Agent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    thread_id: str
    """线程 ID"""
    mcp_client: MultiServerMCPClient = None
    """MCP 客户端"""
    mcp_server_names: List[str] = None
    """MCP 服务名称列表"""
    prompt: str = None
    """提示词"""
    json_store: JsonStore = None
    """JSON 存储"""

    def model_post_init(self,ctx):
        """初始化"""
        if not settings.llm_api_key:
            raise ValueError("LLM API 密钥不能为空")
        if not settings.llm_base_url:
            raise ValueError("LLM 基础 URL 不能为空")
        if not settings.llm_model:
            raise ValueError("LLM 模型不能为空")

        self._load_mcp_client()
        self._load_prompt()
        self._load_json_store()

    def _load_mcp_client(self):
        """加载 MCP 客户端"""
        if Path(settings.mcp_path).exists():
            with open(settings.mcp_path, "r", encoding="utf-8") as f:
                mcp_metadata = json.load(f)
            mcp_servers: dict = mcp_metadata.get("mcpServers", {})

            # 默认值
            mcp_servers = {k: v|{
                "transport": "stdio",
            } for k,v in mcp_servers.items()}
        else:
            mcp_servers = {}

        self.mcp_client = MultiServerMCPClient(mcp_servers)
        self.mcp_server_names = mcp_servers.keys()

        AgentCreate.trigger(thread_id=self.thread_id)

    def _load_prompt(self):
        """加载提示词"""
        if Path(settings.prompt_path).exists():
            with open(settings.prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
        else:
            prompt = ""
        self.prompt = prompt

    def _load_json_store(self):
        """加载 JSON 存储"""
        self.json_store = JsonStore(Path(settings.data_dir) / self.thread_id / settings.memory_file_name)

    def _load_memory(self) -> List[BaseMessage]:
        """加载记忆"""
        metadata: dict = self.json_store.read()
        try:
            messages = simple_to_messages(metadata)
        except:
            logger.exception("加载记忆失败")
            return []
        return messages

    def _save_memory(self,messages:List[BaseMessage]):
        """保存记忆"""
        metadata = messages_to_simple(messages)
        self.json_store.write(metadata)

    def _append_memory(self,message:BaseMessage):
        """追加记忆"""
        self._save_memory(self._load_memory()+[message])

    async def run(self,query:str,user_name:str="user") -> str:
        """运行一轮对话
        Args:
            query: 用户问题
            name: 用户名称
        Returns:
            对话结果
        """
        UserQuery.trigger(query=query,name=user_name)

        async with AsyncExitStack() as stack:
            # 同时持有所有服务器的 session
            sessions = {}
            for name in self.mcp_server_names:
                session = await stack.enter_async_context(self.mcp_client.session(name))
                sessions[name] = session

            # 合并所有服务器的 tools，用 server_name 做前缀避免重名
            all_tools: List[BaseTool] = []
            for name, session in sessions.items():
                tools = await load_mcp_tools(
                    session,
                    server_name=name,
                    tool_name_prefix=True  # 如 "mcp-tool-web-search_search"
                )
                all_tools.extend(tools)
            all_tools.extend(get_all_tools())

            # 加载工具事件
            tool_names = [tool.name for tool in all_tools]
            LoadMCPTools.trigger(tool_names=tool_names)

            # 加载 LLM
            llm = ChatOpenAI(
                model=settings.llm_model,
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )

            # 记录用户消息
            human_content = f"[{user_name}]: {query}"
            self._append_memory(HumanMessage(content=human_content))

            agent = create_agent(
                model=llm,
                tools=all_tools,
                system_prompt=self.prompt,
            )

            response = await self._astream(agent, self._load_memory())

            # AI 回答
            self._append_memory(AIMessage(content=response))
            AssistantResponse.trigger(content=response)

            return response

    async def _astream(self, agent: CompiledStateGraph, messages: list[BaseMessage]) -> str:
        """
        流式执行 agent，并实时触发 CallTool、ToolResponse 回调。
        返回最终 AI 回复文本。
        """
        from langchain_core.messages import AIMessage, ToolMessage
        from ai_hub_agents.callback import ToolCall, ToolResponse

        last_response = ""

        async for mode, chunk in agent.astream(
            {"messages": messages},
            stream_mode=["updates", "values"],
        ):
            if mode == "updates":
                for _node, update in chunk.items():
                    for msg in update.get("messages", []):
                        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                            for tc in msg.tool_calls:
                                ToolCall.trigger(
                                    tool_name=tc.get("name", ""),
                                    args=tc.get("args", {}),
                                )
                        elif isinstance(msg, ToolMessage):
                            ToolResponse.trigger(tool_name=getattr(msg, "name", ""), result=msg.content)
            elif mode == "values":
                msgs = chunk.get("messages", [])
                if msgs:
                    last_response = getattr(msgs[-1], "content", "") or ""

        return last_response