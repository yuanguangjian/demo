"""App 侧设备绑定：bind/unbind/getMeta/checkSign/updateSnSecret 等。

取自 `utils/ipc_bind.py`；**修复**原文件里 `getBindInfo` 重复定义的问题，
保留参数签名更明确、与 App 其他方法风格一致的那一个版本。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import time
import urllib.parse
from typing import Any, Dict, Optional

from common.config import env_base_url
from common.crypto.ecc import gen_key
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import ascii_sort, sign as ecc_sign
from common.utils.json_store import get_sn_secret, save_sn_secret

_logger = get_logger(__name__)


class Bind:
    def __init__(self, env: str) -> None:
        self.env = env
        self.client = HttpClient(env_base_url(env))
        self.headers: Dict[str, str] = {
            "x-ugreen-app-system": "IoS",
            "content-type": "application/json",
            "countryCode": "CN",
            "language": "zh-Hans",
            "app_user_id": "1326011",
        }

    def _signed_params(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        info = get_sn_secret(model, sn, self.env)
        if not info:
            _logger.warning("密钥不存在：%s/%s", model, sn)
            return None
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": info["version"],
        }
        data["sign"] = ecc_sign(data, info["privateKey"])
        return data

    # ---------- 查询 ----------

    def get_app_info(self) -> Optional[Dict[str, Any]]:
        return self.client.request_json("GET", "/app/v1/variety/getAppInfo?platform=rtcx", headers=self.headers)

    def check_sn(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/checkSn",
            headers=self.headers,
            json_body={"productSerialNo": model, "sn": sn},
        )

    def get_bind_info(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        """原文件里本方法定义两次，这里合并为一个版本。"""
        return self.client.request_json(
            "POST",
            "/app/v1/variety/getBindInfo",
            headers=self.headers,
            json_body={"sn": sn, "productSerialNo": model},
        )

    def get_meta(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        data = self._signed_params(sn, model)
        if not data:
            return None
        data["deviceType"] = "ipc_camera"
        data["productSerialNo"] = model
        return self.client.request_json("POST", "/app/v1/variety/getMeta", headers=self.headers, json_body=data)

    def check_sign(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        data = self._signed_params(sn, model)
        if not data:
            return None
        return self.client.request_json("POST", "/app/v1/variety/checkSign", headers=self.headers, json_body=data)

    def device_list(self) -> Optional[Dict[str, Any]]:
        return self.client.request_json("GET", "/app/v1/variety/deviceList", headers=self.headers)

    # ---------- 绑定/解绑 ----------

    def update_device_info(self, name: str, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/updateDeviceInfo",
            headers=self.headers,
            json_body={"deviceName": name, "deviceUniqueCode": sn, "productSerialNo": model},
        )

    def unbind(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/app/v1/variety/unbind",
            headers=self.headers,
            json_body={
                "deviceType": "ipc_camera",
                "deviceUniqueCode": sn,
                "extra": {},
                "productSerialNo": model,
            },
        )

    def bind(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        sign_data = self._signed_params(sn, model)
        if not sign_data:
            return None
        return self.client.request_json(
            "POST",
            "/app/v1/variety/bind",
            headers=self.headers,
            json_body={
                "deviceMac": sn,
                "deviceType": "ipc_camera",
                "deviceUniqueCode": sn,
                "productSerialNo": model,
                "extra": sign_data,
            },
        )

    def get_bind_token(self) -> Optional[str]:
        result = self.client.request_json("GET", "/app/v1/variety/getBindToken", headers=self.headers)
        if result and result.get("code") == 100000:
            return result["data"]["bindToken"]
        return None

    def bind_by_token(self, sn: str, model: str, bind_token: str) -> Optional[Dict[str, Any]]:
        data = self._signed_params(sn, model)
        if not data:
            return None
        data["bindToken"] = bind_token
        return self.client.request_json("POST", "/app/v1/variety/bindByToken", headers=self.headers, json_body=data)

    def get_bind_token_result(self, token: str) -> Optional[Dict[str, Any]]:
        token = urllib.parse.quote(token)
        return self.client.request_json(
            "GET",
            f"/app/v1/variety/getBindTokenResult?bindToken={token}",
            headers=self.headers,
        )

    def update_sn_secret(self, sn: str, model: str, new_version: str) -> Optional[Dict[str, Any]]:
        info = get_sn_secret(model, sn, self.env)
        if not info:
            _logger.warning("密钥不存在：%s/%s", model, sn)
            return None
        new_private, new_public = gen_key()
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": new_version,
            "oldVersion": info["version"],
            "publicKey": new_public,
        }
        data["sign"] = ecc_sign(data, info["privateKey"])
        result = self.client.request_json(
            "POST", "/app/v1/variety/updateSnSecret", headers=self.headers, json_body=data
        )
        if result and result.get("code") == 100000:
            save_sn_secret(
                f"{model}_{sn}",
                {"privateKey": new_private, "publicKey": new_public, "version": new_version},
                self.env,
            )
        return result


if __name__ == "__main__":
    ipc = Bind("local")
    ipc.unbind("I50000U57Q200017", "00000")
