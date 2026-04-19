"""OPPO 开放平台评论抓取（原 `data/oppo.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict

from common.logger import get_logger

from .base import MarketReviewScraper

_logger = get_logger(__name__)


_CONTENT_CURL = """curl 'https://open.oppomobile.com/resource/comment/list.json' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'Cookie: firstLoginTokenForTT=true; isLogin=1; OPPOSID=K-3OTVD8UC1kZGnpwIaFRjTlnJfXWLjD7rBnOdnCe_8GwVgmX7ZOWlJ5FW1CHFVdkEEUw-xYRYM; openplat=084c0de69023686549ebd51c4717a97f' \
  -H 'Origin: https://open.oppomobile.com' \
  -H 'Referer: https://open.oppomobile.com/home/management/app-admin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw 'page=1&app_id=31704887&level=0&content=&from_datetime=&to_datetime=&cp_order=&cp_sort=&replied=' \
  --compressed"""

_SCORE_CURL = """curl 'https://open.oppomobile.com/resource/comment/index.json' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'Cookie: firstLoginTokenForTT=true; isLogin=1; OPPOSID=K-3OTVD8UC1kZGnpwIaFRjTlnJfXWLjD7rBnOdnCe_8GwVgmX7ZOWlJ5FW1CHFVdkEEUw-xYRYM; openplat=084c0de69023686549ebd51c4717a97f' \
  -H 'Origin: https://open.oppomobile.com' \
  -H 'Referer: https://open.oppomobile.com/home/management/app-admin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw 'app_id=31704887' \
  --compressed"""


class OppoScraper(MarketReviewScraper):
    content_curl = _CONTENT_CURL
    score_curl = _SCORE_CURL


_default = OppoScraper()


def getContent() -> Dict[str, Any]:  # noqa: N802
    return _default.fetch_content()


def getCore() -> Dict[str, Any]:  # noqa: N802
    return _default.fetch_score()


if __name__ == "__main__":
    _logger.info(getContent())
    _logger.info(getCore())
