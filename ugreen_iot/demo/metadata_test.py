"""工厂/元数据接口 demo（合并 `测试接口-metadata.py` 与 `_TEST.py`）。

_TEST 多出的 `snSubmitTest` / `switchState` / `getSnByMac` 作为本文件的方法。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import sys
import time
from typing import Any, Dict, Optional

from common.crypto.ecc import gen_key
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import sign as ecc_sign
from common.utils.json_store import save_account

_logger = get_logger(__name__)


class MetadataFactoryClient:
    def __init__(self, base: str, *, app_system: str = "ios") -> None:
        self.client = HttpClient(base)
        self.headers = {"x-ugreen-app-system": app_system, "content-type": "application/json"}

    def _post(self, path: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.client.request_json("POST", path, headers=self.headers, json_body=data)

    def sn_submit(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._post("/metadata/v1/factory/snSubmit", data)

    def sn_submit_test(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._post("/metadata/v1/factory/snSubmitTest", data)

    def switch_state(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._post("/metadata/v1/factory/switchState", data)

    def get_sn_by_mac(self, mac: str, product_model: str) -> Optional[Dict[str, Any]]:
        return self.client.request_json(
            "GET",
            f"/metadata/v1/factory/getSn?mac={mac}&productModel={product_model}",
            headers=self.headers,
        )


def _build_submit_payload(sn: str, product_model: str, client_id: str, client_secret: str) -> Dict[str, Any]:
    private_key, public_key = gen_key()
    version = "1.0.0"
    nonce = int(time.time() * 1000)
    data = {
        "mac": sn,
        "nonce": nonce,
        "productModel": product_model,
        "publicKey": public_key,
        "sn": sn,
        "version": version,
    }
    data["sign"] = ecc_sign(data, private_key)
    data["clientId"] = client_id
    data["timestamp"] = nonce
    data["clientSign"] = ecc_sign(data, client_secret)
    save_account(sn, {"privateKey": private_key, "publicKey": public_key, "version": version}, file="key.json")
    return data


def main(argv: list[str]) -> None:
    sub = argv[1] if len(argv) > 1 else "submitTest"
    base = "http://localhost:9021"
    sn = "I50000U58Q3000AA"
    product_model = "010004"
    client_id = "HaxUIUiF1wVJXEK2OQGJHQ=="
    client_secret = (
        "MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCBWKiQrr6JWXCBcedM0BFD1OCdEhv+YPw3y0bbv05NY9g=="
    )
    client = MetadataFactoryClient(base)
    payload = _build_submit_payload(sn, product_model, client_id, client_secret)

    if sub == "submit":
        _logger.info(client.sn_submit(payload))
    elif sub == "submitTest":
        _logger.info(client.sn_submit_test(payload))
    elif sub == "switch":
        _logger.info(client.switch_state(payload))
    elif sub == "getSn":
        _logger.info(client.get_sn_by_mac("I50000U58Q300098", "010001"))
    else:
        _logger.info("可选子命令: submit | submitTest | switch | getSn")


if __name__ == "__main__":
    main(sys.argv)
