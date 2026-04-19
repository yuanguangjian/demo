"""vivo 开发者中心评论抓取（原 `data/vivo.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict

from common.logger import get_logger

from .base import MarketReviewScraper

_logger = get_logger(__name__)


_CONTENT_CURL = """curl 'https://dev.vivo.com.cn/webapi/comment/info/list?timestamp=1751608727527' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: b_account_username=v7Wf3wBcfM9BfB8CB0Q6KQ%3D%3D; b_account_aid=s9oXesI7rcg%3D; b_account_token=33172ca3e57108a1c1525bf5e326e7ca.1751090349380; JSESSIONID=09B762E8789732241A9C0E47A3D55BDE' \
  -H 'Origin: https://dev.vivo.com.cn' \
  -H 'Referer: https://dev.vivo.com.cn/comment/tab/appStoreDetails?id=603017&packageName=com.ugreen.iot&appType=1' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'csrfToken: nBBGv7' \
  -H 'v-source: 2c3057c01591e7aa94805e6435cddd50' \
  --data-raw '{"model":"","starRating":"","appVersion":"","endDate":"2025-07-04 23:59:59","startDate":"2025-06-03 00:00:00","currentPageNum":1,"pageSize":10,"packageName":"com.ugreen.iot","sort":2,"replyStatus":""}' \
  --compressed"""

_SCORE_CURL = """curl 'https://dev.vivo.com.cn/webapi/comment/info/app?packageName=com.ugreen.iot&timestamp=1751608751509' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: b_account_username=v7Wf3wBcfM9BfB8CB0Q6KQ%3D%3D; JSESSIONID=6DB3CBD9BF91844851EB2A62295FDCB0' \
  -H 'Referer: https://dev.vivo.com.cn/comment/tab/appStoreDetails?id=603017&packageName=com.ugreen.iot&appType=1' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'csrfToken: YZRZX0' \
  -H 'v-source: 0c1726dd402d1d50c417e46e479e6cdc' \
  --compressed"""


class VivoScraper(MarketReviewScraper):
    content_curl = _CONTENT_CURL
    score_curl = _SCORE_CURL


_default = VivoScraper()


def getContent() -> Dict[str, Any]:  # noqa: N802
    return _default.fetch_content()


def getCore() -> Dict[str, Any]:  # noqa: N802
    return _default.fetch_score()


if __name__ == "__main__":
    _logger.info(getContent())
    _logger.info(getCore())
