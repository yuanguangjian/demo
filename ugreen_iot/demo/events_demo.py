"""事件操作记录 demo（原 `ipc项目/ipc-操作记录.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from ugreen_iot.app.event_record import EventRecord


if __name__ == "__main__":
    bearer = (
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjMwODI3MzYsImV4cCI6MTc2MzIwMjczNn0"
        ".8xds39UwjSuaRTg7QQaLKpEl0ai0YoSjS0uWN3u7jaE"
    )
    event = EventRecord("dev", bearer=bearer)
    event.list("I50000U57Q2100OP", "Camera001", page=1, size=10)
