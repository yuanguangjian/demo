"""统一日志配置：业务模块调 `get_logger(__name__)` 即可。"""
from __future__ import annotations

import logging
import os
import sys
from typing import Optional

_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_LEVEL = os.environ.get("DEMO_LOG_LEVEL", "INFO").upper()
_configured = False


def _configure_root() -> None:
    global _configured
    if _configured:
        return
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        root.addHandler(handler)
    root.setLevel(getattr(logging, _DEFAULT_LEVEL, logging.INFO))
    _configured = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    _configure_root()
    return logging.getLogger(name or "demo")
