"""场景：多轮记忆 — 验证 ChatAgent 的对话上下文和 thread 隔离。"""

from __future__ import annotations


class TestMemory:

    def test_remember_name(self, agent_with_memory, renderer):
        """记住用户名字。"""
        tid = "memory-name-test"
        agent_with_memory.invoke("我叫小明", thread_id=tid, callbacks=[renderer])
        result = agent_with_memory.invoke(
            "我叫什么名字？", thread_id=tid, callbacks=[renderer]
        )
        assert "小明" in result

    def test_remember_preference(self, agent_with_memory, renderer):
        """记住用户偏好。"""
        tid = "memory-pref-test"
        agent_with_memory.invoke(
            "我最喜欢的编程语言是 Python", thread_id=tid, callbacks=[renderer]
        )
        result = agent_with_memory.invoke(
            "我最喜欢什么编程语言？", thread_id=tid, callbacks=[renderer]
        )
        assert "Python" in result or "python" in result

    def test_follow_up_reference(self, agent_with_memory, renderer):
        """基于上轮追问，能正确引用上下文。"""
        tid = "memory-followup-test"
        agent_with_memory.invoke(
            "常见的排序算法有哪些？", thread_id=tid, callbacks=[renderer]
        )
        result = agent_with_memory.invoke(
            "其中哪种时间复杂度最优？", thread_id=tid, callbacks=[renderer]
        )
        assert len(result) > 10
        assert any(
            kw in result
            for kw in ["排序", "O(", "复杂度", "快速", "归并", "堆", "sort"]
        )

    def test_thread_isolation(self, agent_with_memory, renderer):
        """不同 thread_id 的对话互相隔离。"""
        tid_a = "isolation-thread-a"
        tid_b = "isolation-thread-b"
        agent_with_memory.invoke(
            "我的名字是爱丽丝", thread_id=tid_a, callbacks=[renderer]
        )
        result = agent_with_memory.invoke(
            "我叫什么名字？", thread_id=tid_b, callbacks=[renderer]
        )
        assert "爱丽丝" not in result
