"""场景：完整工作流 — 一次性完成多项操作。"""

from .conftest import invoke


class TestEndToEndWorkflow:

    def test_full_report(self, agent, xlsx_env, renderer):
        """Agent 一次性完成：排序 + 汇总 + 格式化 + 条件高亮。"""
        result, wb = invoke(
            agent,
            "帮我完成以下操作：\n"
            "1. 按销售额从高到低排序\n"
            "2. 在最后添加合计行，求下单次数和销售额的总和\n"
            "3. 表头加粗并加蓝色背景\n"
            "4. 冻结表头行",
            xlsx_env,
            renderer,
        )
        ws = wb["Sheet1"]
        assert ws["A1"].font.bold is True
        assert ws.freeze_panes is not None
