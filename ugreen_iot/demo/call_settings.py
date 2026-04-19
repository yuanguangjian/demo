"""通话设置/联系人 demo（原 `ipc项目/ipc_通话设置.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from ugreen_iot.app.contact import Contact


if __name__ == "__main__":
    bearer = (
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjExODA1NDAsImV4cCI6MTc2MTMwMDU0MH0"
        ".3aLhyjOHIH3Vcg5ENsCodCjWEEdKfgiKJSRnp3Sy88s"
    )
    contact = Contact("dev", bearer=bearer)
    contact.get_open_id_by_label("I50000U58Q300098", "Camera001", "朋友")
    contact.get_device_all_open_id("I50000U58Q300098", "Camera001")
