"""场景：填写和修改数据 — 让 Agent 写入数据和公式。"""

from .conftest import invoke


class TestEditData:

    def test_add_summary_row(self, agent, xlsx_env, renderer):
        """Agent 能在最后一行添加汇总公式。"""
        result, wb = invoke(
            agent,
            "在数据最后一行的下方添加合计行，计算下单次数、退货人数、销售额的总和",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        found_total = False
        for row in ws.iter_rows(min_row=2, max_col=5):
            if row[0].value and "合计" in str(row[0].value):
                found_total = True
                break
        assert found_total

    def test_find_and_replace(self, agent, xlsx_env, renderer):
        """Agent 能执行查找替换。"""
        result, wb = invoke(
            agent,
            "把所有的'口红'替换为'美妆'",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        values = [ws.cell(row=r, column=2).value for r in range(2, 9)]
        assert "口红" not in values
        assert "美妆" in values
