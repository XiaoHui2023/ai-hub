"""Python 代码执行工具（注入 State 路径）。"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import Annotated

from langchain_core.tools import ToolException, tool
from langgraph.prebuilt import InjectedState

from ._helpers import get_input_file, get_output_file, with_file_lock

logger = logging.getLogger(__name__)


@tool
@with_file_lock
def execute_python(
    state: Annotated[dict, InjectedState],
    code: str,
) -> str:
    """执行 Python 代码进行 Excel 文件操作。

    可用库：openpyxl、pandas、pathlib。通过 print() 输出结果。

    代码中可通过环境变量获取文件路径：
    - os.environ['INPUT_FILE']  — 输入文件的绝对路径
    - os.environ['OUTPUT_FILE'] — 输出文件的绝对路径

    Args:
        code: 要执行的 Python 代码
    """
    env = os.environ.copy()
    env["INPUT_FILE"] = get_input_file(state)
    env["OUTPUT_FILE"] = get_output_file(state)

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    except subprocess.TimeoutExpired as e:
        msg = "execute_python: 代码执行超时（120s）"
        logger.error(msg)
        raise ToolException(msg) from e

    output = result.stdout
    if result.stderr:
        output += f"\nStderr:\n{result.stderr}"
    if result.returncode != 0:
        logger.warning("execute_python: 代码执行失败 (exit %d)", result.returncode)
        output = f"[执行失败] Exit code {result.returncode}:\n{output}"
    return output or "(无输出)"
