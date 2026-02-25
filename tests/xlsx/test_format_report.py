"""场景：美化报表 — 让 Agent 添加格式。"""

from .conftest import invoke


class TestFormatReport:

    def test_bold_header_and_freeze(self, agent, xlsx_env, renderer):
        """Agent 能给表头加粗并冻结首行。"""
        result, wb = invoke(
            agent,
            "把表头行加粗，字号设为14，并冻结首行",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        assert ws["A1"].font.bold is True
        assert ws.freeze_panes is not None

    def test_fill_background(self, agent, xlsx_env, renderer):
        """Agent 能给表头添加背景色。"""
        result, wb = invoke(
            agent,
            "给表头行（第一行）添加蓝色背景",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        assert ws["A1"].fill.fill_type == "solid"
