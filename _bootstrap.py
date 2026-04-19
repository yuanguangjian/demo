"""为脚本直接运行（python path/to/xxx.py）时准备 sys.path。

Usage::

    from _bootstrap import *  # noqa

或在脚本顶部::

    import _bootstrap  # noqa: F401

模块 import 时自动把 demo/ 加入 sys.path，使 `from common.xxx import ...` 在
`python xxx.py` 和 `python -m demo.xxx.yyy` 两种运行方式下都可用。
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_demo_root_in_syspath() -> Path:
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    return here


DEMO_ROOT = _ensure_demo_root_in_syspath()
