"""场景：搜索路径 — 验证 QaAgent 对需要搜索的问题走搜索再回答。"""

from __future__ import annotations


class TestSearchPath:

    def test_realtime_question_with_search(self, agent, renderer):
        """实时性问题应搜索后回答，包含相关关键词。"""
        result = agent.invoke("2026年有哪些重要的AI进展？", callbacks=[renderer])
        assert isinstance(result, str)
        assert len(result) > 50
        assert any(kw in result for kw in ["AI", "人工智能", "模型", "技术"])

    def test_news_question(self, agent, renderer):
        """新闻类问题搜索后有实质内容。"""
        result = agent.invoke("最近有什么科技新闻？", callbacks=[renderer])
        assert isinstance(result, str)
        assert len(result) > 30

    def test_version_comparison(self, agent, renderer):
        """具体版本对比问题。"""
        result = agent.invoke(
            "Python 3.12 和 3.11 相比有哪些改进？", callbacks=[renderer]
        )
        assert isinstance(result, str)
        assert any(kw in result for kw in ["Python", "3.12", "改进", "新", "特性", "性能"])
