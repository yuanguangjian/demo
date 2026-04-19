"""直接 `python .../app/xxx.py` 时把仓库根（含 `common/`）加入 sys.path。

脚本目录仅为 `app/` 时无法解析 `demo/_bootstrap.py`，故须在本包内先执行此模块。
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_demo_root() -> Path:
    p = Path(__file__).resolve().parent
    for _ in range(16):
        if (p / "common").is_dir() and (p / "_bootstrap.py").is_file():
            s = str(p)
            if s not in sys.path:
                sys.path.insert(0, s)
            return p
        if p.parent == p:
            break
        p = p.parent
    raise RuntimeError(
        "找不到 demo 仓库根目录（需要同时存在 common/ 与 _bootstrap.py）"
    )


_ensure_demo_root()
