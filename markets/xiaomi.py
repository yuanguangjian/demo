"""小米应用商店评论抓取（合并 `data/xiaomi.py` 与 `修复数据.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict

from common.logger import get_logger

from .base import CurlRequest, MarketReviewScraper, extract_curl_info  # noqa: F401

_logger = get_logger(__name__)


_CONTENT_CURL = """curl 'https://dev.mi.com/uiueapi/comment/usercomment/commentlist?packageName=com.ugreen.iot&limit=8&offset=0&score=&versionName=&startTime=1748966400000&endTime=1751558400000&model=&searchKeyWords=&mideveloper_ph=d%2F6SAg0NhUqV4Bc21bJaMg%3D%3D&userId=2549403030' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: uLocale=zh_CN; pageType=1; openPlatform=0; JSESSIONID=aaa1tTYQ6fFrwblSKqoFz; serviceToken=Xv5lATucFWfMVEEue0csFBQ87B9/XpWSb/2dNk1mHlEJzjIZujS6kMTyMkikEuJLyBC0RMO8qV8YDyOzA7EporKg0hchiHB5a+EX6td/CH0xbFopFIxa2m7s70QxCDkH9TC4NbSqTG260CM9acb8X3ltNKd+STu6I6u/ngigSSkG5pbqfETHdFWAEFxJ34vtfZalZhLErAfbhCF46QJuh+HRI3i1S9wLfExQp6YGqzameAQVWJSQV6j5hPfaUAlVyAOe/+1RdPiV6VwPf2ujlNFabLIo3uO4LJbPDrdZ+kkBjZXWEQ3by0PcQnTkgbXo13YVnzwh3GxpM6QRK3qG/Gs940mU0dAUZu+DBejAQuw=; userId=2549403030; mideveloper_slh=X7hf5etxGuI/fIz99rcF2n1q24o=; mideveloper_ph=d/6SAg0NhUqV4Bc21bJaMg==' \
  -H 'Referer: https://dev.mi.com/distribute/app/2882303761520310413/comment?packageName=com.ugreen.iot&namespaceValue=0&userId=2549403030' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'x-package-name: com.ugreen.iot' \
  --compressed"""

_SCORE_CURL = """curl 'https://dev.mi.com/uiueapi/comment/usercomment/scores?packageName=com.ugreen.iot&mideveloper_ph=d%2F6SAg0NhUqV4Bc21bJaMg%3D%3D&userId=2549403030' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: uLocale=zh_CN; pageType=1; openPlatform=0' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'x-package-name: com.ugreen.iot' \
  --compressed"""


class XiaomiScraper(MarketReviewScraper):
    content_curl = _CONTENT_CURL
    score_curl = _SCORE_CURL


# 向后兼容：原 data/xiaomi.py 以顶层函数提供
_default = XiaomiScraper()


def getContent() -> Dict[str, Any]:  # noqa: N802 - 保留旧命名兼容
    return _default.fetch_content()


def getCore() -> Dict[str, Any]:  # noqa: N802
    return _default.fetch_score()


def debug_extract_curl() -> None:
    """原 `修复数据.py` 的调试流程：仅打印 curl 解析结果 + 发起一次 GET。"""
    raw = CurlRequest.parse(_CONTENT_CURL)
    _logger.info("URL: %s", raw.url)
    _logger.info("Headers: %s", raw.headers)
    _logger.info("Data: %s", raw.data)
    _logger.info("Response: %s", _default._send(raw))


if __name__ == "__main__":
    _logger.info(getContent())
    _logger.info(getCore())
