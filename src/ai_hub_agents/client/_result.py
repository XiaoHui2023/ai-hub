"""Agent 调用结果数据类。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentResult:
    """``invoke()`` 的返回值，包含文本结果和可选的文件附件。"""

    text: str = ""
    files: dict[str, bytes] = field(default_factory=dict, repr=False)
    _filenames: dict[str, str] = field(default_factory=dict, repr=False)

    def __str__(self) -> str:
        return self.text

    def has_file(self, field_name: str) -> bool:
        """是否包含指定字段的文件。"""
        return field_name in self.files

    def save_file(self, field_name: str, path: str | Path) -> Path:
        """将附件保存到本地文件。

        Returns:
            写入的文件路径。

        Raises:
            KeyError: 不存在该字段的文件。
        """
        if field_name not in self.files:
            raise KeyError(f"No file for field '{field_name}'")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(self.files[field_name])
        return p
