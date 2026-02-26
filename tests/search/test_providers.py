"""SearchResult 数据类和 Provider 注册表测试。"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from ai_hub_agents.search.providers import list_available, resolve_provider
from ai_hub_agents.search.providers.base import SearchResult


class TestSearchResult:

    def test_required_fields(self):
        r = SearchResult(url="https://example.com", title="Example")
        assert r.url == "https://example.com"
        assert r.title == "Example"

    def test_optional_fields_default(self):
        r = SearchResult(url="https://example.com", title="T")
        assert r.published_date is None


class TestProviderRegistry:

    def test_list_available_contains_bocha(self):
        available = list_available()
        assert "bocha" in available

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="未知"):
            resolve_provider("nonexistent_provider")

    def test_missing_api_key_raises(self):
        with patch.dict(os.environ, {"BOCHA_API_KEY": ""}, clear=False):
            with pytest.raises(ValueError, match="不可用"):
                resolve_provider("bocha")

    def test_resolve_with_key(self):
        with patch.dict(os.environ, {"BOCHA_API_KEY": "test-key"}):
            provider = resolve_provider("bocha")
            assert provider.name == "bocha"
