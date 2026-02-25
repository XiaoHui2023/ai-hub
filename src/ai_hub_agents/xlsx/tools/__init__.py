"""xlsx 工具集 — 统一导出。"""

from .cell_ops import clear_range, read_cells, write_cells, write_range
from .chart_ops import create_chart
from .data_ops import (
    add_conditional_format,
    add_data_validation,
    copy_range,
    find_replace,
    sort_range,
)
from .excel_read import read_excel, read_input
from .execute_python import execute_python
from .formatting import (
    auto_fit_columns,
    format_cells,
    freeze_panes,
    merge_cells,
    set_column_width,
    set_row_height,
    unmerge_cells,
)
from .office_xml import pack_office, unpack_office, validate_office
from .recalc import recalc_formulas
from .row_col_ops import delete_cols, delete_rows, insert_cols, insert_rows
from .sheet_ops import add_sheet, copy_sheet, list_sheets, remove_sheet, rename_sheet

ALL_TOOLS = (
    # 读取
    read_input,
    read_excel,
    read_cells,
    # 单元格写入
    write_cells,
    write_range,
    clear_range,
    # 工作表管理
    list_sheets,
    add_sheet,
    remove_sheet,
    rename_sheet,
    copy_sheet,
    # 行列操作
    insert_rows,
    delete_rows,
    insert_cols,
    delete_cols,
    # 格式化
    format_cells,
    set_column_width,
    set_row_height,
    merge_cells,
    unmerge_cells,
    freeze_panes,
    auto_fit_columns,
    # 数据操作
    find_replace,
    copy_range,
    sort_range,
    add_conditional_format,
    add_data_validation,
    # 图表
    create_chart,
    # 公式重算
    recalc_formulas,
    # XML 操作
    unpack_office,
    pack_office,
    validate_office,
    # 兜底
    execute_python,
)

for _t in ALL_TOOLS:
    _t.handle_tool_error = True

__all__ = [t.name for t in ALL_TOOLS] + ["ALL_TOOLS"]
