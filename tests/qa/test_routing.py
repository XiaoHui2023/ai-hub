"""_route_after_router 纯函数测试。"""

from __future__ import annotations

from ai_hub_agents.qa import _route_after_router


class TestRouteAfterRouter:

    def test_needs_search_true(self):
        assert _route_after_router({"qa_needs_search": True}) == "search"

    def test_needs_search_false(self):
        assert _route_after_router({"qa_needs_search": False}) == "chat"

    def test_missing_field_defaults_chat(self):
        assert _route_after_router({}) == "chat"
