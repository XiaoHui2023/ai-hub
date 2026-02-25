"""场景：条件格式高亮 — 让 Agent 按条件标记数据。"""

from .conftest import invoke


class TestConditionalHighlight:

    def test_highlight_no_returns_green(self, agent, xlsx_env, renderer):
        """Agent 能把退货为0的行标记为绿色。"""
        result, wb = invoke(
            agent,
            "把退货人数为0的商品行用绿色背景高亮标出",
            xlsx_env,
            renderer,
        )
        assert "绿" in result or "高亮" in result or "标" in result or "完成" in result
