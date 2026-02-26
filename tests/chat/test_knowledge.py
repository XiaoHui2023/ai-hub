"""场景：知识问答 — 验证 ChatAgent 回答事实性和概念性问题的能力。"""

from __future__ import annotations


class TestKnowledge:

    def test_factual_question(self, agent, renderer):
        """事实性问题应包含关键数据。"""
        result = agent.invoke("太阳从哪个方向升起？", callbacks=[renderer])
        assert "东" in result

    def test_concept_explanation(self, agent, renderer):
        """解释概念时应有实质内容。"""
        result = agent.invoke("什么是机器学习？", callbacks=[renderer])
        assert len(result) > 20
        assert any(kw in result for kw in ["数据", "学习", "模型", "算法", "训练"])

    def test_concise_when_asked(self, agent, renderer):
        """要求简短回答时不长篇大论。"""
        result = agent.invoke("用一句话回答：水的化学式是什么？", callbacks=[renderer])
        assert "H2O" in result or "H₂O" in result
        assert len(result) < 200
