"""通用 Agent 客户端 SDK。

需要安装 ``httpx``::

    pip install ai-hub-agents[client]

Usage::

    from ai_hub_agents.client import AgentClient

    client = AgentClient("http://localhost:8000")
    result = client.invoke("你好", thread_id="s1")
    print(result)
"""

try:
    import httpx as _httpx  # noqa: F401
except ImportError as e:
    raise ImportError(
        "httpx is required for ai_hub_agents.client. "
        "Install with: pip install ai-hub-agents[client]"
    ) from e

from ._async import AsyncAgentClient
from ._event import AgentEvent
from ._result import AgentResult
from ._sync import AgentClient

__all__ = [
    "AgentClient",
    "AsyncAgentClient",
    "AgentEvent",
    "AgentResult",
]
