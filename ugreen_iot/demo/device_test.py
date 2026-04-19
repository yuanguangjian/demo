"""工厂上报 SN demo（原 `ipc项目/设备测试接口.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import time

from common.crypto.ecc import gen_key
from common.http_client import HttpClient
from common.logger import get_logger
from common.signing.ecc_ugreen import sign as ecc_sign
from common.utils.json_store import save_account

_logger = get_logger(__name__)


def sn_submit(*, base: str, sn: str, product_model: str, client_id: str, client_secret: str) -> None:
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

    with HttpClient(base) as client:
        resp = client.post("/metadata/v1/factory/snSubmit", headers={"Content-Type": "application/json"}, json_body=data)
        _logger.info("snSubmit: %s", resp.text)

    save_account(sn, {"privateKey": private_key, "publicKey": public_key, "version": version}, file="key.json")


if __name__ == "__main__":
    sn_submit(
        base="https://iot-test.ugreeniot.com",
        sn="I50000U57Q1100P2",
        product_model="010001",
        client_id="/UqvcYdkFJA1RIajPWEy9Q==",
        client_secret="MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCAMTGHKSzp/VIEZ608mGHgNlw4fOuVA6ia3yXUmN1x0Tg==",
    )
