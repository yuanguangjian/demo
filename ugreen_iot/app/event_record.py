"""IPC 事件记录（取自 `utils/ipc_event_record.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict, Optional

from common.config import env_base_url
from common.http_client import HttpClient

_DEFAULT_BEARER = (
    "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
    ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjg4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyODgwMDAiLCJpYXQiOjE3NjUxNzUzMDgsImV4cCI6MTc2NTI5NTMwOH0"
    ".HGyaYzJt7tSjXWOoaHrnGtZzMx4IoZyL6n1ar8wZ4oE"
)


class EventRecord:
    def __init__(self, env: str, *, bearer: str = _DEFAULT_BEARER) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.headers: Dict[str, str] = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "x-ugreen-app-deviceType": "OPPO R9S",
            "Authorization": bearer,
        }

    def add(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/ipc/eventRecord/add",
            headers=self.headers,
            json_body={"sn": sn, "productSerialNo": model},
        )

    def list(self, sn: str, model: str, page: int, size: int) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"/app/v1/variety/ipc/eventRecord/list?sn={sn}&productSerialNo={model}&size={size}&page={page}",
            headers=self.headers,
        )


if __name__ == "__main__":
    EventRecord("dvt").list("I50001B5J6200024", "010001", 2, 20)
