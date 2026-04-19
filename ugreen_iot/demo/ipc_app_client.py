"""四合一 IPC App 客户端 demo。

合并 `ipc项目/` 下的：
- `测试接口-IPC_TEST.py`（/app/v1/variety/*）
- `openAPI.py`       （/api/v1/meta/*）
- `ID500.py`         （/app/v1/ipc/*, /rpc/v1/ipc/device/*）
- `ipc.py`           （简化版：IpcClient）

抽象出 `IPCAppClient`：同一组业务方法 + 可切换 `prefix`。`__main__` 里演示三套 demo 流程。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import json
import time
import urllib.parse
from typing import Any, Dict, Optional

from common.crypto.ecc import gen_key
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import sign as ecc_sign
from common.utils.json_store import get_sn_secret as _get_sn_secret, save_sn_secret as _save_sn_secret

_logger = get_logger(__name__)


class IPCAppClient:
    """绿联 App 接口统一客户端。切换 `prefix` 适配不同网关 path 前缀。"""

    def __init__(
        self,
        base_url: str,
        user_id: str,
        token: str,
        *,
        prefix: str = "/app/v1/variety",
        factory_prefix: str = "/metadata/v1/factory",
        app_system: str = "ios",
        country_code: str = "CN",
        language: str = "zh-Hans",
    ) -> None:
        self.client = HttpClient(base_url)
        self.prefix = prefix
        self.factory_prefix = factory_prefix
        self.headers: Dict[str, str] = {
            "authorization": token,
            "x-ugreen-app-system": app_system,
            "content-type": "application/json",
            "app_user_id": user_id,
            "countryCode": country_code,
            "language": language,
        }

    def _get(self, path: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json("GET", path, headers=self.headers)

    def _post(self, path: str, body: Any) -> Optional[Dict[str, Any]]:
        return self.client.request_json("POST", path, headers=self.headers, json_body=body)

    @staticmethod
    def _build_signed(sn: str, mac: str, model: str, version: str, private_key: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": version,
        }
        data["sign"] = ecc_sign(data, private_key)
        return data

    # ---------- 设备相关 ----------

    def get_app_info(self, platform: str = "rtcx") -> Optional[Dict[str, Any]]:
        return self._get(f"{self.prefix}/getAppInfo?platform={platform}")

    def check_sn(self, sn: str, model: str, *, device_type: str = "ipc_camera") -> Optional[Dict[str, Any]]:
        return self._post(
            f"{self.prefix}/checkSn",
            {"productSerialNo": model, "sn": sn, "deviceType": device_type},
        )

    def get_meta(self, sn: str, mac: str, model: str, version: str, private_key: str, device_type: str = "ipc_camera") -> Optional[Dict[str, Any]]:
        data = self._build_signed(sn, mac, model, version, private_key)
        data["deviceType"] = device_type
        data["productSerialNo"] = model
        return self._post(f"{self.prefix}/getMeta", data)

    def check_sign(self, sn: str, mac: str, model: str, version: str, private_key: str) -> Optional[Dict[str, Any]]:
        return self._post(
            f"{self.prefix}/checkSign",
            self._build_signed(sn, mac, model, version, private_key),
        )

    def device_list(self) -> Optional[Dict[str, Any]]:
        return self._get(f"{self.prefix}/deviceList")

    def update_device_info(self, sn: str, model: str, name: str) -> Optional[Dict[str, Any]]:
        return self._post(
            f"{self.prefix}/updateDeviceInfo",
            {"deviceName": name, "deviceUniqueCode": sn, "productSerialNo": model},
        )

    def unbind(self, sn: str, model: str, *, device_type: str = "ipc_camera", path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """ID500 变体使用 `/rpc/v1/ipc/device/unBind`，可通过 `path` 覆盖。"""
        return self._post(
            path or f"{self.prefix}/unbind",
            {"deviceType": device_type, "deviceUniqueCode": sn, "extra": {}, "productSerialNo": model},
        )

    def bind(
        self,
        sn: str,
        mac: str,
        model: str,
        version: str,
        private_key: str,
        *,
        device_type: str = "ipc_camera",
        path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        sign_data = self._build_signed(sn, mac, model, version, private_key)
        return self._post(
            path or f"{self.prefix}/bind",
            {
                "deviceMac": mac,
                "deviceType": device_type,
                "deviceUniqueCode": sn,
                "productSerialNo": model,
                "extra": sign_data,
            },
        )

    def get_bind_token(self) -> Optional[str]:
        result = self._get(f"{self.prefix}/getBindToken")
        if result and result.get("code") == 100000:
            return result["data"]["bindToken"]
        return None

    def bind_by_token(self, sn: str, mac: str, model: str, version: str, private_key: str, bind_token: str) -> Optional[Dict[str, Any]]:
        data = self._build_signed(sn, mac, model, version, private_key)
        data["bindToken"] = bind_token
        return self._post(f"{self.prefix}/bindByToken", data)

    def get_bind_token_result(self, token: str) -> Optional[Dict[str, Any]]:
        return self._get(f"{self.prefix}/getBindTokenResult?bindToken={urllib.parse.quote(token)}")

    def get_bind_info(self, sn: str, model: str) -> Optional[Dict[str, Any]]:
        return self._post(f"{self.prefix}/getBindInfo", {"sn": sn, "productSerialNo": model})

    def update_sn_secret(self, sn: str, mac: str, model: str, old_version: str, new_version: str, private_key: str) -> Optional[Dict[str, Any]]:
        new_private, new_public = gen_key()
        data = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": new_version,
            "oldVersion": old_version,
            "publicKey": new_public,
        }
        data["sign"] = ecc_sign(data, private_key)
        result = self._post(f"{self.prefix}/updateSnSecret", data)
        if result and result.get("code") == 100000:
            _save_sn_secret(
                f"{model}_{sn}",
                {"privateKey": new_private, "publicKey": new_public, "version": new_version},
                "device",
            )
        return result

    # ---------- 工厂：上报 SN ----------

    def sn_submit_test(self, sn: str, model: str, *, version: str = "1.0.0", client_id: str = "xxxx") -> Optional[Dict[str, Any]]:
        private_key, public_key = gen_key()
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "publicKey": public_key,
            "sn": sn,
            "version": version,
        }
        data["sign"] = ecc_sign(data, private_key)
        data["clientSign"] = data["sign"]
        data["clientId"] = client_id
        data["timestamp"] = int(time.time() * 1000)
        result = self._post(f"{self.factory_prefix}/snSubmitTest", data)
        if result and result.get("code") == 100000:
            _save_sn_secret(
                f"{model}_{sn}",
                {"privateKey": private_key, "publicKey": public_key, "version": version},
                "device",
            )
        return result

    # ---------- OAuth ----------

    def get_auth_code(self, client_id: str) -> Optional[Dict[str, Any]]:
        return self._post(
            "/app/v1/oauth/authorize",
            {"client_id": client_id, "response_type": "code", "state": str(int(time.time() * 1000))},
        )


def _variety_demo() -> None:
    """等价于 `测试接口-IPC_TEST.py` 的主流程。"""
    sn = "I50000U58Q3000AA"
    model = "010004"
    base = "http://localhost:9010"
    token = (
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIzMzIyMDAxIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJVUyIsImp0aSI6IjMzMjIwMDEiLCJpYXQiOjE3NjMxMDc3MDUsImV4cCI6MTc2MzIyNzcwNX0"
        ".awgVy2DhzFTqB4QUBa7RE3s9JWFBkMBJ1a0xl2p4z1A"
    )
    client = IPCAppClient(base, user_id="1314002", token=token)
    if not _get_sn_secret(model, sn, "device"):
        _logger.info("sn=%s 公私钥不存在", sn)
        client.sn_submit_test(sn, model)
    info = _get_sn_secret(model, sn, "device") or {}
    _logger.info("sn=%s privateKey=%s", sn, info.get("privateKey"))
    client.device_list()


def _meta_demo() -> None:
    """等价于 `openAPI.py` 的主流程（`/api/v1/meta/*`）。"""
    sn = "I50000U58Q300098"
    model = "Camera001"
    base = "http://localhost:9023"
    token = (
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjI4NjEzNTYsImV4cCI6MTc2Mjk4MTM1Nn0"
        ".DNgDAu56NV8-BZnGh-R_A9vtmDjXsSY9_4N3WU6s3oA"
    )
    client = IPCAppClient(base, user_id="1268000", token=token, prefix="/api/v1/meta")
    if not _get_sn_secret(model, sn, "device"):
        client.sn_submit_test(sn, model)
    info = _get_sn_secret(model, sn, "device") or {}
    client.check_sn(sn, model)
    if info:
        client.get_meta(sn, sn, model, info["version"], info["privateKey"])


def _ipc_variant_demo() -> None:
    """等价于 `ID500.py` 的主流程（`/app/v1/ipc/*` + `/rpc/v1/ipc/device/*`）。"""
    sn = "I50000U58Q300098"
    model = "Camera001"
    base = "http://localhost:9017"
    token = (
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjI4NjEzNTYsImV4cCI6MTc2Mjk4MTM1Nn0"
        ".DNgDAu56NV8-BZnGh-R_A9vtmDjXsSY9_4N3WU6s3oA"
    )
    client = IPCAppClient(base, user_id="1268000", token=token, prefix="/app/v1/ipc")
    if not _get_sn_secret(model, sn, "device"):
        client.sn_submit_test(sn, model)
    info = _get_sn_secret(model, sn, "device") or {}
    client.check_sn(sn, model)
    if info:
        client.bind(sn, sn, model, info["version"], info["privateKey"], path="/rpc/v1/ipc/device/bind")


if __name__ == "__main__":
    _variety_demo()
    # _meta_demo()
    # _ipc_variant_demo()
