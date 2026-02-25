# AI Hub

模块化 AI Agent 框架，基于 LangChain / LangGraph。

每个 Agent 都可以独立运行，也可以作为 **工具** 或 **节点** 嵌入更大的工作流。

## 安装

```bash
pip install ai-hub-agents
```

按需安装可选依赖：

```bash
pip install ai-hub-agents[xlsx]      # Excel 处理
pip install ai-hub-agents[server]    # SSE 服务端
```

## 环境配置

复制 `.env.example` 为 `.env` 并填入你的 API 配置：

```bash
cp .env.example .env
```

## 快速开始

### Examples

示例位于 `examples/` 目录，每个子目录对应一个 Agent，均可通过 `python -m` 直接运行：

```bash
python -m examples.<agent_name>

# 查看可用参数
python -m examples.<agent_name> -h
```

### Tests

测试位于 `tests/` 目录，使用 pytest 运行。集成测试需要真实 LLM 调用，请确保 `.env` 已配置。

```bash
# 运行所有测试
pytest tests/

# 运行指定 Agent 的测试
pytest tests/<agent_name>/
```
