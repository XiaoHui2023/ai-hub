"""场景：数据分析 — 让 Agent 排序和统计。"""

from .conftest import invoke


class TestDataAnalysis:

    def test_sort_by_revenue(self, agent, xlsx_env, renderer):
        """Agent 能按销售额降序排列。"""
        result, wb = invoke(
            agent,
            "把数据按销售额从高到低排序",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        first = ws["E2"].value
        second = ws["E3"].value
        assert first is not None and second is not None
        assert first >= second
