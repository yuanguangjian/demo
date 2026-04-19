"""App 侧设备分享 & 消息：qrCode、accountShare、homeList、cancel、msgList 等。

取自 `utils/ipc_share.py`；**修复**原 `cancel()` 方法中 `data` 未定义导致的 NameError。
"""
from __future__ import annotations

import _demo_syspath  # noqa: F401

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import base64
from typing import Any, Dict, Optional, Tuple

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from common.config import env_base_url
from common.http_client import HttpClient
from common.logger import get_logger

_logger = get_logger(__name__)

_MAX_ENCRYPT_BLOCK = 256


class Share:
    def __init__(self, env: str) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.headers: Dict[str, str] = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
        }

    def get_sid_info(self) -> Optional[Tuple[str, str]]:
        j = self.client.request_json("POST", "/app/v1/user/security/getSidInfo", headers=self.headers, json_body={})
        if j and j.get("code") == 100000:
            return j["data"]["sid"], j["data"]["publicKey"]
        return None

    @staticmethod
    def encode_data(raw: str, public_key_b64: str) -> str:
        key = RSA.import_key(base64.b64decode(public_key_b64))
        cipher = PKCS1_v1_5.new(key)
        encrypted = bytearray()
        data = raw.encode("utf-8")
        offset = 0
        while offset < len(data):
            chunk = data[offset : offset + _MAX_ENCRYPT_BLOCK]
            encrypted.extend(cipher.encrypt(chunk))
            offset += _MAX_ENCRYPT_BLOCK
        return base64.b64encode(encrypted).decode("utf-8")

    # ---------- 账号 ----------

    def check_account(self, phone: str, sid: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/user/checkAccount",
            headers=self.headers,
            json_body={"sid": sid, "account": phone},
        )

    # ---------- 二维码分享 ----------

    def qr_code(self, sn: str, model: str, role: str, permission: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/share/qrCode",
            headers=self.headers,
            json_body={
                "productSerialNo": model,
                "deviceUniqueCode": sn,
                "role": role,
                "permission": permission,
            },
        )

    def qr_code_info(self, qr_code: str, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/share/qrCodeInfo",
            headers=self.headers,
            json_body={"qrCode": qr_code, "productSerialNo": model, "deviceUniqueCode": sn},
        )

    def qr_code_receive(self, qr_code: str, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "app/v1/variety/share/qrCodeReceive",
            headers=self.headers,
            json_body={"qrCode": qr_code, "productSerialNo": model, "deviceUniqueCode": sn},
        )

    # ---------- 账号分享 ----------

    def account_share(self, sn: str, model: str, role: str, permission: str, receiver: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "app/v1/variety/share/account",
            headers=self.headers,
            json_body={
                "productSerialNo": model,
                "deviceUniqueCode": sn,
                "role": role,
                "permission": permission,
                "receiver": receiver,
            },
        )

    def home_list(self) -> Optional[Dict[str, Any]]:
        return self.client.request_json("GET", "app/v1/variety/share/homeList", headers=self.headers)

    def receive(self, share_id: int, share_status: int) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "app/v1/variety/share/receive",
            headers=self.headers,
            json_body={"id": share_id, "shareStatus": share_status},
        )

    def share_list(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"app/v1/variety/share/shareList?deviceUniqueCode={sn}&productSerialNo={model}",
            headers=self.headers,
        )

    def cancel(self, share_id: int) -> Optional[Dict[str, Any]]:
        """取消分享。修复：原实现引用未定义的 `data` 变量会抛 NameError。"""
        return self.client.request_json(
            "POST",
            f"app/v1/variety/share/cancel/{share_id}",
            headers=self.headers,
            json_body={},
        )

    def device_info(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"app/v1/variety/share/deviceInfo?deviceUniqueCode={sn}&productSerialNo={model}",
            headers=self.headers,
        )

    def device_info_by_id(self, share_id: int) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"app/v1/variety/share/deviceInfoById?id={share_id}",
            headers=self.headers,
        )

    def msg_list(self, page: int = 1, size: int = 100) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"/app/v1/variety/message/pagination?page={page}&size={size}",
            headers=self.headers,
        )


if __name__ == "__main__":
    Share("dev")
