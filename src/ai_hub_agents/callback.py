from __future__ import annotations
from pydantic import BaseModel
from typing import ClassVar, Callable, Any
        
class Callback(BaseModel):
    """
    回调

    定义回调结构时：
        class A(Callback):
            attr: type

    触发回调时：
        A(attr=value)

    为函数注册回调时：
        @A
        def func(cb:A):
            pass
    """
    functions: ClassVar[dict[str, Callable]] = {}
    """注册的函数列表"""

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and callable(args[0]):
            func = args[0]

            # 注册函数
            if self.__class__.__name__ not in self.__class__.functions:
                self.__class__.functions[self.__class__.__name__] = []
            self.__class__.functions[self.__class__.__name__].append(func)
        else:
            super().__init__(*args, **kwargs)

            field_names = list(self.__class__.model_fields.keys())
            for i, arg in enumerate(args):
                if i < len(field_names):
                    setattr(self, field_names[i], arg)
            
            for key, value in kwargs.items():
                if key in field_names:
                    setattr(self, key, value)
            
            # 触发回调
            for func in self.functions.get(self.__class__.__name__, []):
                func(self)

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

__all__ = [
    "Callback",
    "LoadMCPTools",
    "ToolCall",
    "ToolResponse",
    "UserQuery",
    "AssistantResponse",
    "AgentCreate",
]