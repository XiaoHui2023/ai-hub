"""场景：查看数据 — 让 Agent 读取并描述 Excel 内容。"""

from .conftest import invoke


class TestViewData:

    def test_describe_table_content(self, agent, xlsx_env, renderer):
        """Agent 能读取数据并描述表格内容。"""
        result, wb = invoke(agent, "读取输入文件，告诉我有哪些列和多少行数据", xlsx_env, renderer)
        assert "商品" in result or "品类" in result or "销售" in result
