import threading
import time
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class KeyPool:
    """
    线程安全的 API Key 轮询池

    - 轮询（Round-Robin）选取 key
    - 失败标记 + 冷却自动恢复
    - 所有 key 都冷却时强制放行
    """

    def __init__(self, keys: List[str], cooldown: float = 60.0):
        """
        keys: API Key 列表
        cooldown: 失败后冷却时间（秒），冷却期间跳过该 key
        """
        self._keys = list(keys)
        self._index = 0
        self._lock = threading.Lock()
        self._cooldown = cooldown
        self._failed: dict[str, float] = {}  # key -> 失败时间戳

    def __len__(self) -> int:
        return len(self._keys)

    def __bool__(self) -> bool:
        return bool(self._keys)

    def _is_available(self, key: str) -> bool:
        """检查 key 是否可用（未失败或已过冷却期）"""
        if key not in self._failed:
            return True
        if time.time() - self._failed[key] >= self._cooldown:
            del self._failed[key]
            return True
        return False

    def next(self) -> Optional[str]:
        """轮询获取下一个可用的 key，返回 None 表示池为空"""
        if not self._keys:
            return None

        with self._lock:
            n = len(self._keys)
            # 第一轮：尝试找到一个可用的 key
            for _ in range(n):
                key = self._keys[self._index % n]
                self._index += 1
                if self._is_available(key):
                    return key

            # 所有 key 都在冷却中，清除失败状态并强制返回
            logger.warning("所有 API key 均在冷却中，强制使用下一个")
            self._failed.clear()
            key = self._keys[self._index % n]
            self._index += 1
            return key

    def report_failure(self, key: str):
        """报告某个 key 调用失败，进入冷却期"""
        with self._lock:
            self._failed[key] = time.time()
            suffix = key[-6:] if len(key) > 6 else key
            logger.warning(f"API key ...{suffix} 标记为失败，冷却 {self._cooldown}s")
