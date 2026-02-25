"""LangChain tools for Excel / Office file operations."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

_SCRIPTS_DIR = Path(__file__).parent / "scripts"


@tool
def read_excel(
    file_path: str,
    sheet_name: Optional[str] = None,
    max_rows: int = 50,
) -> str:
    """读取 Excel 文件内容，返回数据预览。

    Args:
        file_path: Excel 文件路径（.xlsx / .xlsm / .csv / .tsv）
        sheet_name: 指定工作表名称，不指定则读取所有工作表
        max_rows: 最大返回行数，默认 50
    """
    import pandas as pd

    path = Path(file_path)
    if not path.exists():
        return f"Error: 文件不存在 {file_path}"

    try:
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            preview = df.head(max_rows).to_string()
            return (
                f"Sheet: {sheet_name}\n"
                f"Shape: {df.shape}\n"
                f"Columns: {list(df.columns)}\n\n{preview}"
            )

        all_sheets = pd.read_excel(file_path, sheet_name=None)
        parts = []
        for name, df in all_sheets.items():
            preview = df.head(max_rows).to_string()
            parts.append(
                f"=== Sheet: {name} | Shape: {df.shape} "
                f"| Columns: {list(df.columns)} ===\n{preview}"
            )
        return "\n\n".join(parts)
    except Exception as e:
        return f"Error: {e}"


@tool
def execute_python(code: str) -> str:
    """执行 Python 代码进行 Excel 文件操作。

    可用库：openpyxl、pandas、pathlib。通过 print() 输出结果。

    Args:
        code: 要执行的 Python 代码
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nStderr:\n{result.stderr}"
        if result.returncode != 0:
            output = f"Exit code {result.returncode}:\n{output}"
        return output or "(无输出)"
    except subprocess.TimeoutExpired:
        return "Error: 代码执行超时（120s）"


@tool
def recalc_formulas(file_path: str, timeout: int = 30) -> str:
    """使用 LibreOffice 重新计算 Excel 文件中的所有公式。

    返回 JSON，包含公式错误详情（#REF!、#DIV/0! 等）。

    Args:
        file_path: Excel 文件路径
        timeout: 超时秒数，默认 30
    """
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS_DIR / "recalc.py"), file_path, str(timeout)],
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS_DIR),
    )
    if result.returncode != 0:
        return f"Error: {result.stderr or result.stdout}"
    return result.stdout


@tool
def unpack_office(input_file: str, output_directory: str) -> str:
    """将 Office 文件（DOCX/PPTX/XLSX）解包到目录，便于 XML 编辑。

    Args:
        input_file: Office 文件路径
        output_directory: 输出目录路径
    """
    result = subprocess.run(
        [
            sys.executable,
            str(_SCRIPTS_DIR / "office" / "unpack.py"),
            input_file,
            output_directory,
        ],
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS_DIR / "office"),
    )
    output = result.stdout.strip()
    if result.returncode != 0:
        output += f"\nError: {result.stderr}"
    return output or result.stderr


@tool
def pack_office(
    input_directory: str,
    output_file: str,
    original_file: Optional[str] = None,
    validate: bool = True,
) -> str:
    """将目录打包为 Office 文件（DOCX/PPTX/XLSX），支持验证和自动修复。

    Args:
        input_directory: 解包后的目录路径
        output_file: 输出文件路径（.docx / .pptx / .xlsx）
        original_file: 原始文件路径，用于验证比较
        validate: 是否执行验证，默认 True
    """
    cmd = [
        sys.executable,
        str(_SCRIPTS_DIR / "office" / "pack.py"),
        input_directory,
        output_file,
    ]
    if original_file:
        cmd.extend(["--original", original_file])
    if not validate:
        cmd.extend(["--validate", "false"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS_DIR / "office"),
    )
    output = result.stdout.strip()
    if result.returncode != 0:
        output += f"\nError: {result.stderr}"
    return output or result.stderr


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
        str(_SCRIPTS_DIR / "office" / "validate.py"),
        path,
    ]
    if auto_repair:
        cmd.append("--auto-repair")
    if original_file:
        cmd.extend(["--original", original_file])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(_SCRIPTS_DIR / "office"),
    )
    output = result.stdout.strip()
    if result.returncode != 0:
        output += f"\nError: {result.stderr}"
    return output or result.stderr
