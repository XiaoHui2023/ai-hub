import importlib.util
from pathlib import Path
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

def load_tools_from_directory(dir_path: str | Path) -> list[BaseTool]:
    """从目录下所有 .py 脚本动态加载并收集所有 BaseTool"""
    dir_path = Path(dir_path)
    tools: list[BaseTool] = []

    for file in dir_path.glob("*.py"):
        if file.name.startswith("_"):
            continue

        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.exception(f"跳过 {file}")
            continue

        # 遍历模块中所有属性
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, BaseTool):
                tools.append(obj)
            # 若用 @tool 装饰，得到的是 StructuredTool，也是 BaseTool 子类

    return tools

def get_all_tools() -> list[BaseTool]:
    """获取所有工具"""
    return load_tools_from_directory(Path(__file__).parent)