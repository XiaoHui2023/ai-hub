"""场景：创建图表 — 让 Agent 生成可视化图表。"""

from .conftest import invoke


class TestCreateChart:

    def test_create_revenue_chart(self, agent, xlsx_env, renderer):
        """Agent 能根据数据创建柱状图。"""
        result, wb = invoke(
            agent,
            "根据商品名称和销售额创建一个柱状图",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        assert len(ws._charts) > 0
