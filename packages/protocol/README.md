# ai-hub-protocol

AI Hub 统一协议定义包，包含各服务接口的请求/响应模型。所有模型基于 [Pydantic v2](https://docs.pydantic.dev/) 构建。

---

## 安装

```bash
pip install ai-hub-protocol
```

从源码安装（开发模式）：

```bash
cd packages/protocol
pip install -e .
```

## 依赖

- Python >= 3.10
- pydantic >= 2.0

---

## 模块结构

```
ai_hub_protocol/
├── __init__.py          # 导出 BaseRequest, BaseResponse, chat, search, context
├── base.py              # BaseRequest / BaseResponse 基类
├── chat/
│   ├── __init__.py
│   └── completion.py    # 聊天补全接口（含 Message 模型）
├── context/
│   ├── __init__.py
│   ├── add.py           # 上下文添加接口
│   └── search.py        # 上下文搜索接口
└── search/
    ├── __init__.py
    └── query.py         # 搜索查询接口
```

---

## API 参考

### 基类 — `ai_hub_protocol.base`

#### `BaseRequest`

所有请求模型的基类。配置了 `extra="forbid"`，不允许传入未定义的字段。

| 字段 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| `provider` | `str` | — | 是 | AI 提供商标识（如 `"openai"`, `"anthropic"`） |
| `model` | `str` | `""` | 否 | 模型名称（如 `"gpt-4"`, `"claude-3"`） |
| `stream` | `bool` | `False` | 否 | 是否启用流式响应 |

```python
from ai_hub_protocol.base import BaseRequest

# 不能直接使用，应通过子类使用
# 所有子类自动继承 provider / model / stream 字段
```

#### `BaseResponse`

所有响应模型的基类。

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str \| list \| dict` | 响应内容，可以是字符串、列表或字典 |

---

### 聊天模块 — `ai_hub_protocol.chat.completion`

用于 AI 聊天补全接口的请求/响应模型。

#### `Message`

聊天消息模型。

| 字段 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| `role` | `Literal["user", "assistant", "system"]` | — | 是 | 消息角色 |
| `content` | `str` | — | 是 | 消息内容 |
| `name` | `Optional[str]` | `None` | 否 | 发送者名称（可选） |

#### `Request`

聊天补全请求。继承自 `BaseRequest`。

| 字段 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| *继承* `provider` | `str` | — | 是 | AI 提供商 |
| *继承* `model` | `str` | `""` | 否 | 模型名称 |
| *继承* `stream` | `bool` | `False` | 否 | 是否流式 |
| `messages` | `List[Message]` | — | 是 | 聊天消息列表 |
| `temperature` | `Optional[float]` | `None` | 否 | 采样温度 |
| `frequency_penalty` | `Optional[float]` | `None` | 否 | 频率惩罚 |
| `presence_penalty` | `Optional[float]` | `None` | 否 | 存在惩罚 |
| `top_p` | `Optional[float]` | `None` | 否 | 核采样参数 |

#### `Response`

聊天补全响应。继承自 `BaseResponse`。

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str` | 模型生成的回复文本 |

#### 使用示例

```python
from ai_hub_protocol.chat.completion import Request, Response, Message

# 构造请求
request = Request(
    provider="openai",
    model="gpt-4",
    stream=False,
    messages=[
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="你好！"),
    ],
    temperature=0.7,
)

# 解析响应
response = Response(content="你好！有什么可以帮你的吗？")
print(response.content)  # "你好！有什么可以帮你的吗？"
```

---

### 搜索模块 — `ai_hub_protocol.search.query`

用于 AI 搜索接口的请求/响应模型。

#### `Request`

搜索请求。继承自 `BaseRequest`。

| 字段 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| *继承* `provider` | `str` | — | 是 | AI 提供商 |
| *继承* `model` | `str` | `""` | 否 | 模型名称 |
| *继承* `stream` | `bool` | `False` | 否 | 是否流式 |
| `query` | `str` | — | 是 | 搜索查询内容 |

#### `Response`

搜索响应。继承自 `BaseResponse`。

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str \| list \| dict` | 搜索结果 |

#### 使用示例

```python
from ai_hub_protocol.search.query import Request, Response

request = Request(
    provider="tavily",
    query="最新的 AI 新闻",
)

# 响应可以是多种格式
response = Response(content=[
    {"title": "AI 新闻 1", "url": "https://..."},
    {"title": "AI 新闻 2", "url": "https://..."},
])
```

---

### 上下文模块 — `ai_hub_protocol.context`

用于上下文管理（知识库/记忆）的请求/响应模型。包含 **添加** 和 **搜索** 两个子接口。

#### 添加上下文 — `ai_hub_protocol.context.add`

##### `Request`

添加上下文请求。继承自 `BaseRequest`。

| 字段 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| *继承* `provider` | `str` | — | 是 | AI 提供商 |
| *继承* `model` | `str` | `""` | 否 | 模型名称 |
| *继承* `stream` | `bool` | `False` | 否 | 是否流式 |
| `content` | `str` | — | 是 | 要添加的上下文内容 |
| `user_id` | `str` | — | 是 | 用户标识 |
| `tag` | `str` | — | 是 | 上下文标签/分类 |

##### `Response`

添加上下文响应。继承自 `BaseResponse`。

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str \| list \| dict` | 操作结果 |

##### 使用示例

```python
from ai_hub_protocol.context.add import Request, Response

request = Request(
    provider="mem0",
    content="用户喜欢 Python 编程",
    user_id="user_123",
    tag="preference",
)
```

---

#### 搜索上下文 — `ai_hub_protocol.context.search`

##### `Request`

搜索上下文请求。继承自 `BaseRequest`。

| 字段 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| *继承* `provider` | `str` | — | 是 | AI 提供商 |
| *继承* `model` | `str` | `""` | 否 | 模型名称 |
| *继承* `stream` | `bool` | `False` | 否 | 是否流式 |
| `query` | `str` | — | 是 | 搜索查询内容 |
| `user_id` | `str` | — | 是 | 用户标识 |
| `tag` | `str` | — | 是 | 上下文标签/分类 |

##### `Response`

搜索上下文响应。继承自 `BaseResponse`。

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `str \| list \| dict` | 搜索到的上下文结果 |

##### 使用示例

```python
from ai_hub_protocol.context.search import Request, Response

request = Request(
    provider="mem0",
    query="用户的编程偏好",
    user_id="user_123",
    tag="preference",
)
```

---

## 导入方式汇总

```python
# 基类
from ai_hub_protocol.base import BaseRequest, BaseResponse
# 或
from ai_hub_protocol import BaseRequest, BaseResponse

# 聊天
from ai_hub_protocol.chat.completion import Request, Response, Message

# 搜索
from ai_hub_protocol.search.query import Request, Response

# 上下文 - 添加
from ai_hub_protocol.context.add import Request, Response

# 上下文 - 搜索
from ai_hub_protocol.context.search import Request, Response
```

> **注意**：由于各模块的 `Request` / `Response` 同名，在同一文件中使用多个模块时，建议通过模块路径区分：
>
> ```python
> from ai_hub_protocol.chat import completion as chat_completion
> from ai_hub_protocol.search import query as search_query
>
> chat_req = chat_completion.Request(provider="openai", messages=[...])
> search_req = search_query.Request(provider="tavily", query="...")
> ```

---

## 设计约定

1. **所有请求继承 `BaseRequest`**：自动包含 `provider`、`model`、`stream` 三个公共字段。
2. **禁止额外字段**：`BaseRequest` 配置了 `extra="forbid"`，传入未定义字段会报错，保证接口严格性。
3. **所有响应继承 `BaseResponse`**：统一包含 `content` 字段。
4. **模块命名规范**：每个子模块（chat、search、context）下的文件定义该接口的 `Request` 和 `Response`。
5. **Pydantic v2**：使用 `model_config = ConfigDict(...)` 而非 v1 的 `class Config`。

---

## 扩展指南

如需添加新接口（例如 `embedding`），按以下步骤：

1. 在 `ai_hub_protocol/` 下创建新目录（如 `embedding/`）
2. 创建 `__init__.py` 导出子模块
3. 创建接口文件（如 `create.py`），定义 `Request`（继承 `BaseRequest`）和 `Response`（继承 `BaseResponse`）
4. 在 `ai_hub_protocol/__init__.py` 中注册新模块

```python
# ai_hub_protocol/embedding/create.py
from typing import List
from ..base import BaseRequest, BaseResponse

class Request(BaseRequest):
    input: str | List[str]

class Response(BaseResponse):
    content: list  # embedding vectors
```
