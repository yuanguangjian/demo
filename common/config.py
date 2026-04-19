"""统一的本地配置读取：

- `load_json(name)`：读取位于 demo/ 根目录的 JSON（如 `env.json`、`mysql.json`）。
- `env_base_url(env)`：按环境名取业务 base URL。
- `get(key, default=None)`：读取进程环境变量。
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

DEMO_ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=None)
def load_json(name: str) -> Dict[str, Any]:
    """读取 demo/ 下指定名称的 JSON 文件，返回 dict。

    允许传入相对路径或绝对路径。找不到文件返回空 dict（便于密钥缺失时降级）。
    """
    path = Path(name)
    if not path.is_absolute():
        path = DEMO_ROOT / name
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name: str, data: Dict[str, Any]) -> None:
    path = Path(name)
    if not path.is_absolute():
        path = DEMO_ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def env_base_url(env: str, cfg_file: str = "env.json") -> str:
    """根据环境名（dev/test/ces...）返回业务 base URL。"""
    envs = load_json(cfg_file)
    if env not in envs:
        raise KeyError(f"环境 '{env}' 未在 {cfg_file} 中定义，可选：{list(envs)}")
    return envs[env]


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    """读取进程环境变量。"""
    return os.environ.get(key, default)
