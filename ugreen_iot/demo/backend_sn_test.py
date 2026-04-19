"""管理后台 SN/产品编辑 接口 demo（原 `ipc项目/后台SN测试.py`）。

修复：原文件引用 `from ipc项目.ipc_通话设置 import productSerialNo` —— 相当于仅是一个
变量 leak，这里直接定义本地变量。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict, Optional

from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import ascii_sort

_logger = get_logger(__name__)


class BackendSnClient:
    def __init__(self, base: str, token: str) -> None:
        self.client = HttpClient(base)
        self.headers = {"authorization": token, "content-type": "application/json"}

    def add(self, product_name: str, product_no: str, product_serial_no: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/admin/v1/variety/sn/productIt/add",
            headers=self.headers,
            json_body={"productName": product_name, "productNo": product_no, "productSerialNo": product_serial_no},
        )

    def edit(self, record_id: str, product_name: str, product_no: str, product_serial_no: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/admin/v1/variety/sn/productIt/edit",
            headers=self.headers,
            json_body={
                "id": record_id,
                "productName": product_name,
                "productSerialNo": product_serial_no,
                "productNo": product_no,
            },
        )

    def delete(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            f"/admin/v1/variety/sn/productIt/del/{record_id}",
            headers=self.headers,
        )

    def list(self, *, page: int = 1, size: int = 10, product_name: str = "", product_no: str = "", product_serial_no: str = "") -> Optional[Dict[str, Any]]:
        qs = ascii_sort(
            {
                "productName": product_name,
                "productNo": product_no,
                "productSerialNo": product_serial_no,
                "page": page,
                "size": size,
            }
        )
        return self.client.request_json("GET", f"/admin/v1/variety/sn/productIt/list?{qs}", headers=self.headers)

    def sn_list(
        self,
        *,
        page: int = 1,
        size: int = 10,
        product_name: str = "",
        sn: str = "",
        first_start_time: str = "",
        first_end_time: str = "",
        scan_start_time: str = "",
        scan_end_time: str = "",
        status: str = "",
    ) -> Optional[Dict[str, Any]]:
        qs = ascii_sort(
            {
                "productName": product_name,
                "sn": sn,
                "firstStartTime": first_start_time,
                "firstEndTime": first_end_time,
                "scanStartTime": scan_start_time,
                "scanEndTime": scan_end_time,
                "status": status,
                "page": page,
                "size": size,
            }
        )
        return self.client.request_json("GET", f"/admin/v1/variety/sn/list?{qs}", headers=self.headers)


if __name__ == "__main__":
    token = (
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxIiwiVVNFUl9DT1VOVFJZX0NPREUiOiIiLCJqdGkiOiIxIiwiaWF0IjoxNzU5OTk4NDk3LCJleHAiOjE3NjAwMDU2OTd9"
        ".4BjML2DpveQjTf8MXcniKWI6VZGkrISEE-PAwnSjJUg"
    )
    client = BackendSnClient("http://localhost:9010", token)
    client.sn_list()
