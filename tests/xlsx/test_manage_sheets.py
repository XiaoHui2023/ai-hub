"""场景：管理工作表 — 让 Agent 创建和操作 sheet。"""

from .conftest import invoke


class TestManageSheets:

    def test_create_summary_sheet(self, agent, xlsx_env, renderer):
        """Agent 能创建新 sheet 并复制数据过去。"""
        result, wb = invoke(
            agent,
            "创建一个名为'汇总'的新工作表，把 Sheet1 的表头复制过去",
            xlsx_env,
            renderer,
        )
        assert "汇总" in wb.sheetnames
