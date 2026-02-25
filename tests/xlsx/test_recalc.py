"""场景：公式重算 — Agent 写入公式后尝试重算应优雅处理。"""

from .conftest import invoke


class TestRecalc:

    def test_write_formula_and_recalc(self, agent, xlsx_env, renderer):
        """Agent 写入汇总公式后整体流程不报错。"""
        result, wb = invoke(
            agent,
            "在E9单元格写入销售额求和公式，然后重算公式",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        found_formula = False
        for row in ws.iter_rows(min_row=2, max_col=5):
            for cell in row:
                if cell.value and str(cell.value).startswith("="):
                    found_formula = True
                    break
        assert found_formula
