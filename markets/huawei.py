"""华为 AGC 评论抓取（原 `data/huawei.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict

from common.logger import get_logger

from .base import MarketReviewScraper

_logger = get_logger(__name__)


_CONTENT_CURL = """curl 'https://agc-drcn.developer.huawei.com/agc/edge/review/v1/manage/developer/reviews/query?entityId=110890551&entityType=1&limit=50&page=1&sort=0&startTime=1743782400000&endTime=1751644799000' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://developer.huawei.com' \
  -H 'Referer: https://developer.huawei.com/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-HD-CSRF: 4201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C' \
  -H 'agcTeamId: 890086200300034431' \
  --data-raw '{"auditStates":[1,3],"countries":["CN"]}' \
  --compressed"""

_SCORE_CURL = """curl 'https://agc-drcn.developer.huawei.com/agc/edge/review/v1/manage/developer/ratingStat?entityId=110890551&entityType=1' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://developer.huawei.com' \
  -H 'Referer: https://developer.huawei.com/' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-HD-CSRF: 4201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C' \
  -H 'agcTeamId: 890086200300034431' \
  --compressed"""


class HuaweiScraper(MarketReviewScraper):
    content_curl = _CONTENT_CURL
    score_curl = _SCORE_CURL


_default = HuaweiScraper()


def getContent() -> Dict[str, Any]:  # noqa: N802
    return _default.fetch_content()


def getCore() -> Dict[str, Any]:  # noqa: N802
    return _default.fetch_score()


if __name__ == "__main__":
    _logger.info(getContent())
    _logger.info(getCore())
