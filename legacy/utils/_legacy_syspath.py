"""直接 `python .../legacy/xxx/yyy.py` 时把 legacy 下几个目录加入 sys.path。

legacy 脚本使用"裸名 import"（如 import EccUtil / rtcxUtil / request），
跨目录引用时原生 sys.path 机制无法解析，此模块负责补齐。

本文件在 utils/ 与 ipc项目/ 下各有一份（内容完全相同），
因为它必须与调用脚本同目录才能被 `import _legacy_syspath` 解析。
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_legacy_dirs() -> Path:
    here = Path(__file__).resolve().parent
    for _ in range(8):
        if here.name == "legacy" and (here / "utils").is_dir():
            for sub in ("utils", "ipc项目"):
                d = here / sub
                if d.is_dir() and str(d) not in sys.path:
                    sys.path.insert(0, str(d))
            return here
        if here.parent == here:
            break
        here = here.parent
    raise RuntimeError("找不到 demo/legacy 根目录")


_ensure_legacy_dirs()
