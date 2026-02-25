"""输出文件自动初始化节点。"""

from __future__ import annotations

import shutil
from pathlib import Path


def auto_init_output(state: dict) -> dict:
    """前置节点：自动初始化输出文件。

    - 输出文件已存在 → 跳过（保留之前的修改）
    - 输入文件存在 → 复制到输出路径
    - 输入文件不存在 → 创建空工作簿
    """
    output = state["output_file"]
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    input_file = state.get("input_file", "")
    if input_file and Path(input_file).exists():
        shutil.copy2(input_file, output)
    else:
        from openpyxl import Workbook

        Workbook().save(output)
    return {}
