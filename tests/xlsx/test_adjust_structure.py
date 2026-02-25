"""场景：调整表结构 — 让 Agent 插入/删除行列。"""

from .conftest import invoke


class TestAdjustStructure:

    def test_insert_header_row(self, agent, xlsx_env, renderer):
        """Agent 能在表头上方插入标题行。"""
        result, wb = invoke(
            agent,
            "在第1行上方插入一行，写入'销售数据报表'作为大标题",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        assert ws["A1"].value is not None
        assert "商品名称" in str(ws["A2"].value or "")
