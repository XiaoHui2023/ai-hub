from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前日期和时间。当需要知道当前时间时使用。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")