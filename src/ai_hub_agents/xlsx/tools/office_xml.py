"""Office 文件 XML 级别操作工具（解包 / 打包 / 验证）。"""

from __future__ import annotations

import sys
from typing import Optional

from langchain_core.tools import tool

from ._helpers import SCRIPTS_DIR, run_script

_OFFICE_DIR = SCRIPTS_DIR / "office"


@tool
def unpack_office(input_file: str, output_directory: str) -> str:
    """将 Office 文件（DOCX/PPTX/XLSX）解包到目录，便于 XML 编辑。

    Args:
        input_file: Office 文件路径
        output_directory: 输出目录路径
    """
    return run_script(
        [sys.executable, str(_OFFICE_DIR / "unpack.py"), input_file, output_directory],
        cwd=_OFFICE_DIR,
    )


@tool
def pack_office(
    input_directory: str,
    output_file: str,
    original_file: Optional[str] = None,
    run_validation: bool = True,
) -> str:
    """将目录打包为 Office 文件（DOCX/PPTX/XLSX），支持验证和自动修复。

    Args:
        input_directory: 解包后的目录路径
        output_file: 输出文件路径（.docx / .pptx / .xlsx）
        original_file: 原始文件路径，用于验证比较
        run_validation: 是否执行验证，默认 True
    """
    cmd = [
        sys.executable,
        str(_OFFICE_DIR / "pack.py"),
        input_directory,
        output_file,
    ]
    if original_file:
        cmd.extend(["--original", original_file])
    if not run_validation:
        cmd.extend(["--validate", "false"])
    return run_script(cmd, cwd=_OFFICE_DIR)


@tool
def validate_office(
    path: str,
    original_file: Optional[str] = None,
    auto_repair: bool = True,
) -> str:
    """验证 Office 文档 XML 文件，检查 XSD 架构合规性。

    Args:
        path: 解包目录或 Office 文件路径
        original_file: 原始文件路径
        auto_repair: 是否自动修复常见问题，默认 True
    """
    cmd = [
        sys.executable,
        str(_OFFICE_DIR / "validate.py"),
        path,
    ]
    if auto_repair:
        cmd.append("--auto-repair")
    if original_file:
        cmd.extend(["--original", original_file])
    return run_script(cmd, cwd=_OFFICE_DIR)
