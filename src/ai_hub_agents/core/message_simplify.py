from langchain_core.messages import BaseMessage
from typing import List
from langchain_core.messages import messages_to_dict, messages_from_dict

def messages_to_simple(messages: List[BaseMessage]) -> list[dict]:
    """BaseMessage 列表 -> LangChain 序列化格式 [{"type", "data"}, ...]"""
    return messages_to_dict(messages)

def simple_to_messages(data: list) -> List[BaseMessage]:
    """LangChain 格式 -> BaseMessage 列表（兼容旧的 role/content 格式）"""
    if not data:
        return []
    first = data[0] if data else {}
    if isinstance(first, dict) and "role" in first and "type" not in first:
        role_to_type = {"user": "human", "assistant": "ai", "system": "system"}
        converted = []
        for item in data:
            role = item.get("role", "user")
            content = item.get("content", "")
            name = item.get("name")
            type_ = role_to_type.get(role, "human")
            converted.append({
                "type": type_,
                "data": {
                    "content": content,
                    "type": type_,
                    "name": name,
                    "additional_kwargs": {},
                    "response_metadata": {},
                },
            })
        data = converted
    return messages_from_dict(data)