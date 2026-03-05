from ai_hub_agents.callback import UserQuery, AssistantResponse, ToolResponse, ToolCall, LoadMCPTools, AgentCreate
import logging

logger = logging.getLogger(__name__)

# ANSI 颜色代码（需在支持 ANSI 的终端或配合 colorama 使用）
R = "\033[0m"       # 重置
C = "\033[1;36m"   # 青色 - 用户
G = "\033[1;32m"   # 绿色 - 助手
Y = "\033[1;33m"   # 黄色 - 工具调用
B = "\033[1;34m"   # 蓝色 - 工具响应
M = "\033[1;35m"   # 洋红 - 加载 MCP


class EventMonitor:
    def __init__(self):
        self.has_load_mcp_tools = False

        @UserQuery
        def _(cb: UserQuery):
            logger.info(f"{C}💬 [用户] {cb.name}: {cb.query}{R}")

        @AssistantResponse
        def _(cb: AssistantResponse):
            preview = cb.content[:100] + ("..." if len(cb.content) > 100 else "")
            logger.info(f"{G}🤖 [助手回复]: {preview}{R}")

        @ToolCall
        def _(cb: ToolCall):
            s_args = " ".join(f"{k}={v}" for k, v in cb.args.items())
            logger.info(f"{Y}🔧 [工具调用] {cb.tool_name} {s_args} {R}")

        @ToolResponse
        def _(cb: ToolResponse):
            s = str(cb.result)
            preview = s[:80] + "..." if len(s) > 80 else s
            logger.info(f"{B}✅ [工具响应] {cb.tool_name}: {preview}{R}")

        @LoadMCPTools
        def _(cb: LoadMCPTools):
            if not self.has_load_mcp_tools:
                self.has_load_mcp_tools = True
            else:
                return
            s_tool_names = " ".join(cb.tool_names)
            logger.info(f"{M}📦 [加载 MCP 工具] {s_tool_names}{R}")

        @AgentCreate
        def _(cb: AgentCreate):
            logger.info(f"{M}📦 [创建代理] {cb.thread_id}{R}")