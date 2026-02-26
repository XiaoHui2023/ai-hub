"""ChatAgent 测试公共 fixture。"""

from __future__ import annotations

import pytest

from ai_hub_agents.chat import ChatAgent
from ai_hub_agents.test import ColorStreamRenderer, load_test_llm, setup_logging


def pytest_configure(config):
    setup_logging()


@pytest.fixture(scope="session")
def llm():
    return load_test_llm()


@pytest.fixture(scope="session")
def agent(llm):
    """整个测试会话复用同一个 agent 实例。"""
    return ChatAgent.create(llm)


@pytest.fixture()
def renderer():
    return ColorStreamRenderer()
