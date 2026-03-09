from __future__ import annotations
from typing import ClassVar, Callable, Any, TypeVar
from fastapi import UploadFile
import asyncio
import logging

logger = logging.getLogger(__name__)
T = TypeVar("T", bound="Callback")

class Callback():
    """
    回调

    定义回调结构时：
        class A(Callback):
            attr: type

    触发回调时：
        cb = A.trigger(attr=value) # 同步
        cb = await A.atrigger(attr=value) # 异步

    为函数注册回调时：
        @A
        def func(cb:A):
            pass
    """
    function_registry: ClassVar[dict[str, list[Callable]]] = {}
    """注册的函数列表"""
    _async: ClassVar[bool] = False
    """是否异步"""

    def __init__(self, *args, **kwargs):
        """初始化"""
        if len(args) == 1 and not kwargs and callable(args[0]):
            func = args[0]
            if self._async != asyncio.iscoroutinefunction(func):
                raise ValueError(f"函数{func}是{'异步' if asyncio.iscoroutinefunction(func) else '同步'}，但回调{self.__class__.__name__}是{'异步' if self._async else '同步'}")
            self.register(func)
        else:
            field_names = list(self.__class__.__annotations__.keys())
            for i, arg in enumerate(args):
                if i < len(field_names):
                    setattr(self, field_names[i], arg)
                else:
                    raise ValueError(f"参数过多[{i}]: {arg}")
            
            for key, value in kwargs.items():
                if key in field_names:
                    setattr(self, key, value)
                else:
                    raise ValueError(f"未知属性[{key}]: {value}")

    @classmethod
    def register(cls, func: Callable):
        """注册函数"""
        if cls.__name__ not in cls.function_registry:
            cls.function_registry[cls.__name__] = []
        cls.function_registry[cls.__name__].append(func)

    @classmethod
    def trigger(cls:type[T],*args,**kwargs) -> T:
        """同步触发回调"""
        self = cls(*args, **kwargs)

        for func in cls.function_registry.get(cls.__name__, []):
            func(self)
        return self

    @classmethod
    async def atrigger(cls:type[T],*args,**kwargs) -> T:
        """异步触发回调"""
        self = cls(*args, **kwargs)

        for func in cls.function_registry.get(cls.__name__, []):
            await func(self)
        return self

class LoadMCPTools(Callback):
    """加载 MCP 工具"""
    tool_names: list[str]
    """工具名称列表"""

class ToolCall(Callback):
    """调用工具"""
    tool_name: str
    """工具名称"""
    args: dict
    """参数"""

class ToolResponse(Callback):
    """工具响应"""
    tool_name: str
    """工具名称"""
    result: Any
    """结果"""

class UserQuery(Callback):
    """用户查询"""
    name: str
    """用户名称"""
    query: str
    """内容"""

class AssistantResponse(Callback):
    """助手响应"""
    content: str
    """内容"""

class AgentCreate(Callback):
    """创建代理"""
    thread_id: str
    """线程ID"""

class APIRequest(Callback):
    """API请求"""
    thread_id: str
    """线程ID"""
    query: str
    """查询"""
    files: list[UploadFile]
    """文件"""
    user_name: str|None = None
    """用户名称"""

class APIResponse(Callback):
    """API响应"""
    thread_id: str
    """线程ID"""
    response: str
    """内容"""
    files: list[str]
    """文件列表"""

class APIRoundtrip(Callback):
    _async: ClassVar[bool] = True
    """API处理往返流程"""
    request: APIRequest
    """请求"""
    response: APIResponse = None
    """响应"""

__all__ = [
    "Callback",
    "LoadMCPTools",
    "ToolCall",
    "ToolResponse",
    "UserQuery",
    "AssistantResponse",
    "AgentCreate",
]