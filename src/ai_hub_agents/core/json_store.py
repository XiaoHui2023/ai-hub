import json
from pathlib import Path
from filelock import FileLock

class JsonStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self._lock_path = Path(str(path) + ".lock")

    def read(self) -> dict:
        with FileLock(self._lock_path, timeout=10):
            if not self.path.exists():
                return {}
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

    def write(self, data: dict) -> None:
        with FileLock(self._lock_path, timeout=10):
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            tmp.replace(self.path)