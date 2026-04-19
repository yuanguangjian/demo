"""元数据网关客户端（JWT 鉴权）：`/api/v1/meta/*`。

取自 `utils/ipc_gateway_metadata.py`。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from typing import Any, Dict, Optional

from common.config import env_base_url
from common.crypto.ecc import gen_key
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.jwt_es256 import generate_es256_token
from common.utils.json_store import get_sn_secret, save_sn_secret

_logger = get_logger(__name__)

_DEFAULT_PRIVATE_KEY = (
    "MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCABytI6RcuA8rqPnkBOqtjmsTk0vL1oPE1jAT/8DO2/ew=="
)


class MetadataGateway:
    def __init__(self, env: str, *, private_key: str = _DEFAULT_PRIVATE_KEY) -> None:
        self.env = env
        base_url = env_base_url(env)
        self.client = HttpClient(base_url)
        self.headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + generate_es256_token(private_key),
        }

    def check_sn(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "POST",
            "/api/v1/meta/checkSn",
            headers=self.headers,
            json_body={"sn": sn, "productModel": product_model},
        )

    def _read_sn(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        info = get_sn_secret(product_model, sn, "device")
        if not info:
            _logger.warning("没有找到密钥：%s/%s", product_model, sn)
        return info

    def get_sn_metadata(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        info = self._read_sn(sn, product_model)
        if not info:
            return None
        return self.client.request_json(
            "POST",
            "/api/v1/meta/getMeta",
            headers=self.headers,
            json_body={"sn": sn, "productModel": product_model, "version": info["version"]},
        )

    def get_sn_secret(self, sn: str, product_model: str) -> Optional[Dict[str, Any]]:
        info = self._read_sn(sn, product_model)
        if not info:
            return None
        return self.client.request_json(
            "POST",
            "/api/v1/meta/getSnSecretV2",
            headers=self.headers,
            json_body={"sn": sn, "productModel": product_model, "version": info["version"]},
        )

    def update_sn_secret(self, sn: str, product_model: str, new_version: str = "1.0.5") -> Optional[Dict[str, Any]]:
        info = self._read_sn(sn, product_model)
        if not info:
            return None
        new_private, new_public = gen_key()
        data = {
            "sn": sn,
            "productModel": product_model,
            "version": new_version,
            "oldVersion": info["version"],
            "publicKey": new_public,
        }
        result = self.client.request_json("POST", "/api/v1/meta/updateSnSecret", headers=self.headers, json_body=data)
        if result and result.get("code") == 100000:
            save_sn_secret(
                f"{product_model}_{sn}",
                {"publicKey": new_public, "version": new_version, "privateKey": new_private},
                "device",
            )
        return result


if __name__ == "__main__":
    gw = MetadataGateway("device")
    gw.check_sn("I50000U57Q200017", "00000")
