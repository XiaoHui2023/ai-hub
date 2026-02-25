"""快捷发布脚本: 构建 → 上传 PyPI"""

import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
PYPROJECT = ROOT / "pyproject.toml"
DIST = ROOT / "dist"

_VER_RE = re.compile(r'(version\s*=\s*)"([^"]+)"')


def run(cmd: str) -> subprocess.CompletedProcess:
    env = {**__import__("os").environ, "PYTHONUTF8": "1"}
    r = subprocess.run(cmd, shell=True, capture_output=True, env=env, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"[FAIL] {cmd}")
        if r.stdout.strip():
            print(r.stdout.strip())
        if r.stderr.strip():
            print(r.stderr.strip())
        sys.exit(1)
    return r


def read_version() -> str:
    m = _VER_RE.search(PYPROJECT.read_text("utf-8"))
    if not m:
        sys.exit("cannot read version from pyproject.toml")
    return m.group(2)


def write_version(ver: str) -> None:
    text = PYPROJECT.read_text("utf-8")
    PYPROJECT.write_text(_VER_RE.sub(rf'\g<1>"{ver}"', text), "utf-8")


def bump_patch(ver: str) -> str:
    parts = ver.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def pypi_versions(name: str) -> set[str]:
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return set(json.loads(resp.read())["releases"].keys())
    except Exception:
        return set()


def main() -> None:
    pkg_name = "ai-hub-agents"
    version = read_version()
    published = pypi_versions(pkg_name)

    while version in published:
        new = bump_patch(version)
        print(f"v{version} already on PyPI, bump -> v{new}")
        version = new

    if version != read_version():
        write_version(version)

    print(f"\n>> publish {pkg_name} v{version}\n")

    if DIST.exists():
        shutil.rmtree(DIST)
    run(f"{sys.executable} -m build {ROOT}")
    for f in DIST.iterdir():
        print(f"   {f.name}  ({f.stat().st_size / 1024:.1f} KB)")

    run(f"{sys.executable} -m twine upload dist/*")
    print(f"\n>> done: {pkg_name} v{version}")


if __name__ == "__main__":
    main()
