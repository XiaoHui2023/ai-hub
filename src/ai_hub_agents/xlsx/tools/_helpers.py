"""工具共享的辅助函数。"""

from __future__ import annotations

import functools
import json
import logging
import subprocess
import threading
from pathlib import Path

from langchain_core.tools import ToolException

logger = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"


def get_input_file(state: dict) -> str:
    """从 state 获取 input_file，自动转为绝对路径。"""
    return str(Path(state["input_file"]).resolve())


def get_output_file(state: dict) -> str:
    """从 state 获取 output_file，自动转为绝对路径。"""
    return str(Path(state["output_file"]).resolve())


_file_lock = threading.Lock()


def with_file_lock(func):
    """装饰器：确保同一时刻只有一个工具操作输出文件。"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with _file_lock:
            return func(*args, **kwargs)

    return wrapper


def ensure_dict(value) -> dict | None:
    """确保值为 dict，LLM 有时会传 JSON 字符串。"""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        raise ToolException(f"无法解析为字典: {value!r}")
    return value


def run_script(
    cmd: list[str], cwd: str | Path | None = None, timeout: int = 120
) -> str:
    """运行子进程并返回输出。失败时抛出 ToolException。"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd
        )
    except subprocess.TimeoutExpired as e:
        msg = f"子进程超时（{timeout}s）: {cmd[0]}"
        logger.error(msg)
        raise ToolException(msg) from e

    output = result.stdout.strip()
    if result.returncode != 0:
        err = result.stderr.strip() or output
        label = Path(cmd[1]).name if len(cmd) > 1 else cmd[0]
        msg = f"{label} 失败 (exit {result.returncode}): {err}"
        logger.error(msg)
        raise ToolException(msg)
    return output
