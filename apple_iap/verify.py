"""Apple 收据 / JWS Payload 验证（原 `apple/appleVerify.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import base64
import json
from typing import Any, Dict

import jwt
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from common.http_client import HttpClient
from common.logger import get_logger

_logger = get_logger(__name__)

PROD_VERIFY_URL = "https://buy.itunes.apple.com/verifyReceipt"
SANDBOX_VERIFY_URL = "https://sandbox.itunes.apple.com/verifyReceipt"
_SHARED_SECRET = "fd014432952249008c1e1531e0cc696a"


def verify_receipt(base64_receipt: str, *, is_sandbox: bool = False, shared_secret: str = _SHARED_SECRET) -> Dict[str, Any]:
    """验证苹果收据。21007 自动回退沙盒。"""
    url = SANDBOX_VERIFY_URL if is_sandbox else PROD_VERIFY_URL
    with HttpClient() as client:
        resp = client.post(
            url,
            headers={"Content-Type": "application/json"},
            json_body={"receipt-data": base64_receipt, "password": shared_secret},
        )
    result: Dict[str, Any] = resp.json() if resp.content else {}
    if result.get("status") == 21007 and not is_sandbox:
        _logger.info("收据实际为沙盒，自动重试")
        return verify_receipt(base64_receipt, is_sandbox=True, shared_secret=shared_secret)
    return result


def parse_signed_payload(signed_payload: str) -> Dict[str, Any]:
    """解析 Apple JWS：验签并返回 payload。"""
    try:
        parts = signed_payload.split(".")
        if len(parts) != 3:
            raise ValueError("非法 JWS：应为 3 段")
        header_json = base64.urlsafe_b64decode(parts[0] + "===").decode("utf-8")
        header = json.loads(header_json)
        x5c = header.get("x5c") or []
        if not x5c:
            raise ValueError("Header 中缺少证书链 x5c")
        first_cert_pem = f"-----BEGIN CERTIFICATE-----\n{x5c[0]}\n-----END CERTIFICATE-----"
        cert = x509.load_pem_x509_certificate(first_cert_pem.encode("utf-8"), default_backend())
        public_key = cert.public_key()
        return jwt.decode(
            signed_payload,
            public_key,
            algorithms=["ES256"],
            audience="appstoreconnect-v1",
            options={"verify_aud": False},
        )
    except Exception as e:
        _logger.exception("解析 JWS 失败：%s", e)
        return {}


if __name__ == "__main__":
    sample = ""
    if sample:
        _logger.info(json.dumps(parse_signed_payload(sample), ensure_ascii=False, indent=4))
