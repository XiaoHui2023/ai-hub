"""Excel 公式重算工具。"""

from __future__ import annotations

import shutil
import sys
from typing import Annotated

from langchain_core.tools import ToolException, tool
from langgraph.prebuilt import InjectedState

from ._helpers import SCRIPTS_DIR, get_output_file, run_script, with_file_lock


def _find_soffice() -> str | None:
    """查找 LibreOffice soffice 可执行文件路径。"""
    if shutil.which("soffice"):
        return "soffice"
    import os
    if os.name == "nt":
        for base in (os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")):
            if base:
                candidate = os.path.join(base, "LibreOffice", "program", "soffice.exe")
                if os.path.isfile(candidate):
                    return candidate
    return None


@tool
@with_file_lock
def recalc_formulas(
    state: Annotated[dict, InjectedState],
    timeout: int = 30,
) -> str:
    """重新计算输出文件中的所有公式（使用 LibreOffice）。

    返回 JSON，包含公式错误详情（#REF!、#DIV/0! 等）。

    Args:
        timeout: 超时秒数，默认 30
    """
    if not _find_soffice():
        return (
            "未找到 LibreOffice，跳过公式重算。"
            "公式已写入文件，用户用 Excel/WPS 打开时会自动重算。"
        )
    file_path = get_output_file(state)
    return run_script(
        [sys.executable, str(SCRIPTS_DIR / "recalc.py"), file_path, str(timeout)],
        cwd=SCRIPTS_DIR,
        timeout=timeout + 10,
    )
