"""Excel 文件读取工具。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Optional

from langchain_core.tools import ToolException, tool
from langgraph.prebuilt import InjectedState

from ._helpers import get_input_file

logger = logging.getLogger(__name__)


def _read_excel_impl(
    file_path: str, sheet_name: str | None = None, max_rows: int = 50
) -> str:
    import pandas as pd

    path = Path(file_path)
    if not path.exists():
        logger.error("文件不存在: %s", file_path)
        raise FileNotFoundError(f"文件不存在: {file_path}")

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
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error("读取 Excel 失败: %s", e)
        raise ToolException(f"读取 Excel 失败: {e}") from e


@tool
def read_input(
    state: Annotated[dict, InjectedState],
    sheet_name: Optional[str] = None,
    max_rows: int = 50,
) -> str:
    """读取输入 Excel 文件内容，返回数据预览。

    Args:
        sheet_name: 指定工作表名称，不指定则读取所有工作表
        max_rows: 最大返回行数，默认 50
    """
    file_path = get_input_file(state)
    result = _read_excel_impl(file_path, sheet_name, max_rows)
    return f"[输入文件路径: {file_path}]\n{result}"


@tool
def read_excel(
    file_path: str,
    sheet_name: Optional[str] = None,
    max_rows: int = 50,
) -> str:
    """读取任意 Excel 文件内容，返回数据预览。

    Args:
        file_path: Excel 文件路径
        sheet_name: 指定工作表名称，不指定则读取所有工作表
        max_rows: 最大返回行数，默认 50
    """
    return _read_excel_impl(file_path, sheet_name, max_rows)
