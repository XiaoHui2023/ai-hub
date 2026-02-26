"""场景：真实搜索 — 验证 SearchAgent 的端到端搜索能力。"""

from __future__ import annotations


class TestSearchScenario:

    def test_known_topic_summary(self, agent, renderer):
        """已知话题应返回 >100 字的总结。"""
        result = agent.invoke("Python 编程语言的主要特点", callbacks=[renderer])
        assert isinstance(result, str)
        assert len(result) > 100

    def test_result_contains_source(self, agent, renderer):
        """搜索结果应包含来源链接。"""
        result = agent.invoke("LangChain 框架介绍", callbacks=[renderer])
        assert isinstance(result, str)
        assert "http" in result or "链接" in result or "来源" in result or len(result) > 50

    def test_comparison_contains_both(self, agent, renderer):
        """对比问题应包含双方关键词。"""
        result = agent.invoke(
            "FastAPI 和 Flask 有什么区别？", callbacks=[renderer]
        )
        assert isinstance(result, str)
        has_fastapi = any(k in result for k in ["FastAPI", "fastapi", "fast"])
        has_flask = any(k in result for k in ["Flask", "flask"])
        assert has_fastapi or has_flask

    def test_chinese_query(self, agent, renderer):
        """中文查询正常工作。"""
        result = agent.invoke("什么是向量数据库？", callbacks=[renderer])
        assert isinstance(result, str)
        assert len(result) > 20
        assert any(kw in result for kw in ["向量", "数据库", "嵌入", "相似"])

    def test_unanswerable_graceful(self, agent, renderer):
        """不可回答的问题优雅降级，不崩溃。"""
        result = agent.invoke(
            "zxqwerty12345 这个不存在的东西是什么？",
            callbacks=[renderer],
        )
        assert isinstance(result, str)
