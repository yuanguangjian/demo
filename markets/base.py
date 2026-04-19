"""各应用市场评论抓取的公共基类与 curl 解析。

抽自 `data/xiaomi.py`、`data/vivo.py`、`data/oppo.py`、`data/huawei.py` —— 去掉四份重复的
`extract_curl_info` 实现。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from common.http_client import HttpClient
from common.logger import get_logger

_logger = get_logger(__name__)


def extract_curl_info(curl_command: str) -> Tuple[Optional[str], Dict[str, str], Optional[str]]:
    """从 curl 复制粘贴文本提取 URL / Header / body。"""
    url_match = re.search(r"curl\s+'([^']+)'", curl_command)
    url = url_match.group(1) if url_match else None

    headers: Dict[str, str] = {}
    for k, v in re.findall(r"-H\s+'([^:]+): ([^']+)'", curl_command):
        headers[k] = v

    data_match = re.search(r"--data-raw\s+'([^']+)'", curl_command)
    data = data_match.group(1) if data_match else None
    return url, headers, data


@dataclass
class CurlRequest:
    url: str
    headers: Dict[str, str]
    data: Optional[str]
    method: str = "GET"

    @classmethod
    def parse(cls, curl_command: str, *, method: Optional[str] = None) -> "CurlRequest":
        url, headers, data = extract_curl_info(curl_command)
        if url is None:
            raise ValueError("未从 curl 中解析出 URL")
        return cls(url=url, headers=headers, data=data, method=method or ("POST" if data else "GET"))


class MarketReviewScraper:
    """所有市场评论抓取脚本的公共父类。

    子类只需提供 `content_curl` 和 `score_curl` 常量，即可：
    - `fetch_content()` / `fetch_score()` 返回 JSON 字典。
    """

    content_curl: str = ""
    score_curl: str = ""

    def __init__(self) -> None:
        self.client = HttpClient(timeout=15.0)

    def _send(self, raw: CurlRequest) -> Dict[str, Any]:
        resp = self.client.request(
            raw.method,
            raw.url,
            headers=raw.headers,
            data=raw.data.encode("utf-8") if raw.data else None,
        )
        try:
            return resp.json()
        except Exception:
            _logger.warning("响应不是合法 JSON: %s", resp.text[:200])
            return json.loads(resp.text)

    def fetch_content(self) -> Dict[str, Any]:
        return self._send(CurlRequest.parse(self.content_curl))

    def fetch_score(self) -> Dict[str, Any]:
        return self._send(CurlRequest.parse(self.score_curl))
