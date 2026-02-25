"""行列操作工具。"""

from __future__ import annotations

from typing import Annotated

from langchain_core.tools import ToolException, tool
from langgraph.prebuilt import InjectedState
from openpyxl import load_workbook

from ._helpers import get_output_file, with_file_lock


def _load(state: dict):
    return load_workbook(get_output_file(state))


@tool
@with_file_lock
def insert_rows(
    state: Annotated[dict, InjectedState],
    sheet_name: str,
    row: int,
    count: int = 1,
) -> str:
    """在指定行之前插入空行。

    Args:
        sheet_name: 工作表名称
        row: 在此行之前插入（1-based）
        count: 插入行数，默认 1
    """
    try:
        wb = _load(state)
        wb[sheet_name].insert_rows(row, count)
        wb.save(get_output_file(state))
        return f"已在第 {row} 行前插入 {count} 行"
    except KeyError:
        raise ToolException(f"工作表 '{sheet_name}' 不存在")
    except Exception as e:
        raise ToolException(f"insert_rows 失败: {e}") from e


@tool
@with_file_lock
def delete_rows(
    state: Annotated[dict, InjectedState],
    sheet_name: str,
    row: int,
    count: int = 1,
) -> str:
    """删除指定的行。

    Args:
        sheet_name: 工作表名称
        row: 起始行号（1-based）
        count: 删除行数，默认 1
    """
    try:
        wb = _load(state)
        wb[sheet_name].delete_rows(row, count)
        wb.save(get_output_file(state))
        return f"已删除第 {row} 行起共 {count} 行"
    except KeyError:
        raise ToolException(f"工作表 '{sheet_name}' 不存在")
    except Exception as e:
        raise ToolException(f"delete_rows 失败: {e}") from e


@tool
@with_file_lock
def insert_cols(
    state: Annotated[dict, InjectedState],
    sheet_name: str,
    col: int,
    count: int = 1,
) -> str:
    """在指定列之前插入空列。

    Args:
        sheet_name: 工作表名称
        col: 列号（1=A, 2=B, ...），在此列之前插入
        count: 插入列数，默认 1
    """
    try:
        wb = _load(state)
        wb[sheet_name].insert_cols(col, count)
        wb.save(get_output_file(state))
        return f"已在第 {col} 列前插入 {count} 列"
    except KeyError:
        raise ToolException(f"工作表 '{sheet_name}' 不存在")
    except Exception as e:
        raise ToolException(f"insert_cols 失败: {e}") from e


@tool
@with_file_lock
def delete_cols(
    state: Annotated[dict, InjectedState],
    sheet_name: str,
    col: int,
    count: int = 1,
) -> str:
    """删除指定的列。

    Args:
        sheet_name: 工作表名称
        col: 起始列号（1=A, 2=B, ...）
        count: 删除列数，默认 1
    """
    try:
        wb = _load(state)
        wb[sheet_name].delete_cols(col, count)
        wb.save(get_output_file(state))
        return f"已删除第 {col} 列起共 {count} 列"
    except KeyError:
        raise ToolException(f"工作表 '{sheet_name}' 不存在")
    except Exception as e:
        raise ToolException(f"delete_cols 失败: {e}") from e
