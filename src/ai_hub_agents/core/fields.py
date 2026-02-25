"""State 字段标注。

通过 Annotated 标记文件类型字段，server 层自动处理上传/下载/临时文件。

重要：使用 InputFile / OutputFile 标注的 state schema 类
不应使用 ``from __future__ import annotations``，否则标注信息无法在运行时读取。
"""


class InputFile:
    """标注输入文件字段。server 层自动将上传文件存入临时目录。"""


class OutputFile:
    """标注输出文件字段。server 层自动创建临时路径并提供下载。

    Args:
        ext: 输出文件扩展名，如 ".xlsx"。
    """

    def __init__(self, ext: str = "") -> None:
        self.ext = ext


def get_file_fields(state_schema: type) -> tuple[list[str], list[str]]:
    """从 state_schema 的 Annotated 标注中提取文件字段。

    Returns:
        (input_field_names, output_field_names)
    """
    if state_schema is None:
        return [], []

    inputs: list[str] = []
    outputs: list[str] = []

    for cls in state_schema.__mro__:
        for name, hint in getattr(cls, "__annotations__", {}).items():
            for meta in getattr(hint, "__metadata__", ()):
                if isinstance(meta, InputFile) and name not in inputs:
                    inputs.append(name)
                elif isinstance(meta, OutputFile) and name not in outputs:
                    outputs.append(name)

    return inputs, outputs


def get_output_extensions(
    state_schema: type,
    output_fields: list[str],
) -> dict[str, str]:
    """从 OutputFile 标注提取扩展名映射。"""
    if state_schema is None:
        return {}

    result: dict[str, str] = {}
    target = set(output_fields)

    for cls in state_schema.__mro__:
        for name, hint in getattr(cls, "__annotations__", {}).items():
            if name not in target or name in result:
                continue
            for meta in getattr(hint, "__metadata__", ()):
                if isinstance(meta, OutputFile) and meta.ext:
                    result[name] = meta.ext

    return result
