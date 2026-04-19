"""统一 HTTP 客户端：

特性：

- 复用 `requests.Session`（连接池）。
- 默认 `timeout`（可全局配置，默认 10 秒）。
- 5xx 自动重试（可关闭）。
- `on_unauthorized` 钩子：401 或 `code==100003` 时调用，刷新 token 后重试一次。
- 统一日志：method / url / status / 耗时。
- 自动 `json.dumps` body 与 JSON 解析。
"""
from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict, Mapping, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logger import get_logger

_logger = get_logger(__name__)

# ``on_unauthorized(headers)`` 应原地更新 headers（常用于注入新的 Authorization）。
ReloginHook = Callable[[Dict[str, str]], None]


class HttpClient:
    def __init__(
        self,
        base_url: str = "",
        *,
        timeout: float = 10.0,
        max_retries: int = 2,
        on_unauthorized: Optional[ReloginHook] = None,
        default_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.on_unauthorized = on_unauthorized
        self.session = requests.Session()
        if default_headers:
            self.session.headers.update(default_headers)

        # 只对幂等方法做自动重试，避免重复写入。
        retry = Retry(
            total=max_retries,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=50)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _full_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}{path}"

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Mapping[str, Any]] = None,
        data: Any = None,
        json_body: Any = None,
        timeout: Optional[float] = None,
        _retry_on_auth: bool = True,
    ) -> requests.Response:
        url = self._full_url(path)
        hdrs: Dict[str, str] = dict(headers or {})

        # 业务约定：json_body 自动序列化为 JSON body。
        body: Any = None
        if json_body is not None:
            body = json.dumps(json_body, ensure_ascii=False)
            hdrs.setdefault("Content-Type", "application/json")
        elif data is not None:
            body = data

        start = time.time()
        resp = self.session.request(
            method=method.upper(),
            url=url,
            headers=hdrs,
            params=params,
            data=body,
            timeout=timeout or self.timeout,
        )
        elapsed = time.time() - start
        _logger.info("%s %s -> %s (%.3fs)", method.upper(), url, resp.status_code, elapsed)

        # HTTP 401 或业务码 100003：token 失效，跑钩子后重试一次。
        if _retry_on_auth and self.on_unauthorized and self._needs_relogin(resp):
            _logger.info("检测到鉴权失败，触发 on_unauthorized 钩子后重试")
            self.on_unauthorized(hdrs)
            return self.request(
                method,
                path,
                headers=hdrs,
                params=params,
                data=data,
                json_body=json_body,
                timeout=timeout,
                _retry_on_auth=False,
            )
        return resp

    @staticmethod
    def _needs_relogin(resp: requests.Response) -> bool:
        if resp.status_code == 401:
            return True
        if resp.status_code == 200:
            try:
                return resp.json().get("code") == 100003
            except ValueError:
                return False
        return False

    # 便捷方法，返回解析后的 JSON（失败时返回 None 并打印响应）。
    def request_json(self, method: str, path: str, **kwargs: Any) -> Optional[Any]:
        resp = self.request(method, path, **kwargs)
        if resp.status_code != 200:
            _logger.warning("非 200 响应: %s %s", resp.status_code, resp.text[:200])
            return None
        try:
            return resp.json()
        except ValueError:
            _logger.warning("响应不是合法 JSON: %s", resp.text[:200])
            return None

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
