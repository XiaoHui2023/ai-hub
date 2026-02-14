# ai-hub-protocol

AI Hub 统一协议定义包，包含各服务接口的请求/响应模型。

## 安装

```bash
pip install ai-hub-protocol
```

从源码安装（开发模式）：

```bash
cd packages/protocol
pip install -e .
```

## 模块结构

```
ai_hub_protocol/
├── base.py              # BaseRequest / BaseResponse 基类
├── chat/
│   └── completion.py    # 聊天补全接口（含 Message 模型）
├── context/
│   ├── add.py           # 上下文添加接口
│   └── search.py        # 上下文搜索接口
└── search/
    └── query.py         # 搜索查询接口
```

## 使用示例

```python
from ai_hub_protocol.base import BaseRequest, BaseResponse
from ai_hub_protocol.chat.completion import Request, Response, Message

# 构造聊天请求
request = Request(
    provider="openai",
    model="gpt-4",
    messages=[
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello!"),
    ],
)
```

## 依赖

- Python >= 3.10
- pydantic >= 2.0
