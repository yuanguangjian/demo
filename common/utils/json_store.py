"""零散 JSON 存储工具：沿用历史文件名 `sn.json`、`account.json` 等。

替代 `utils/fileUtil.py`。
"""
from __future__ import annotations

from typing import Any, Optional

from ..config import load_json, save_json


def save_sn_secret(key: str, value: Any, env: str, file: str = "sn.json") -> None:
    data = load_json(file)
    load_json.cache_clear()
    if env not in data:
        data[env] = {}
    data[env][str(key)] = value
    save_json(file, data)


def get_sn_secret(product_model: str, sn: str, env: str, file: str = "sn.json") -> Optional[Any]:
    key = f"{product_model}_{sn}"
    data = load_json(file)
    return data.get(env, {}).get(key)


def save_account(key: str, value: Any, file: str = "account.json") -> None:
    data = load_json(file)
    load_json.cache_clear()
    data[str(key)] = value
    save_json(file, data)


def get_account(key: str, file: str = "account.json") -> Optional[Any]:
    return load_json(file).get(str(key))
