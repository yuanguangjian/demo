"""App 侧设备分享 demo（原 `ipc项目/ipc_分享.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from ugreen_iot.app.share import Share


if __name__ == "__main__":
    base = "http://127.0.0.1:9010/"
    share = Share("dev")
    share.client.base_url = base.rstrip("/")
    share.headers["authorization"] = (
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjI4MjU3MjIsImV4cCI6MTc2Mjk0NTcyMn0"
        ".vmHgyk5fAuQePsKle_9lzrEcvlS3DtofeGuwnanKHp0"
    )
    share.headers["app_user_id"] = "1314002"
    share.home_list()
