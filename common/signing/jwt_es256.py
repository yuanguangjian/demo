"""ES256 JWT 生成：支持多种常见模板。

覆盖场景：
1. `generate_es256_token(base64_private_key, iss, sub, ttl)` — 自家元数据网关。
2. `generate_apple_connect_token(secret_b64, key_id, issuer_id, ttl)` — App Store Connect REST。
3. `generate_apple_storekit_token(secret_b64, key_id, issuer_id, bundle_id, ttl)` — StoreKit 2。
4. `generate_apple_token_from_pem(pem, key_id, issuer_id, bundle_id, ttl)` — 读 `.p8` 后直接用。

替代 `utils/jwt_token.py`、`apple/appleToken.py`、`pay.py`。
"""
from __future__ import annotations

import base64
import datetime
import time
import uuid
from typing import Optional

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

__all__ = [
    "base64_to_pem",
    "generate_es256_token",
    "generate_apple_connect_token",
    "generate_apple_storekit_token",
    "generate_apple_token_from_pem",
]


def base64_to_pem(base64_key: str) -> str:
    """把 `.p8` 中的 Base64 部分包装成标准 PEM。"""
    chunks = [base64_key[i : i + 64] for i in range(0, len(base64_key), 64)]
    body = "\n".join(chunks)
    return f"-----BEGIN PRIVATE KEY-----\n{body}\n-----END PRIVATE KEY-----\n"


def generate_es256_token(
    base64_private_key: str,
    *,
    iss: str = "ugreen-service",
    sub: str = "ugreen-sign",
    ttl_seconds: int = 60,
) -> str:
    """用 Base64 编码的 DER 私钥生成简单 ES256 JWT（自家元数据网关使用）。"""
    key_bytes = base64.b64decode(base64_private_key)
    private_key = serialization.load_der_private_key(key_bytes, password=None, backend=default_backend())
    payload = {
        "sub": sub,
        "iss": iss,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds),
    }
    return jwt.encode(payload, private_key, algorithm="ES256")


def generate_apple_connect_token(
    secret_b64: str,
    key_id: str,
    issuer_id: str,
    *,
    ttl_seconds: int = 1200,
) -> str:
    """生成 App Store Connect API JWT（aud=appstoreconnect-v1, 不含 iat/nonce/bid）。"""
    pem = base64_to_pem(secret_b64)
    now = int(time.time())
    return jwt.encode(
        {
            "iss": issuer_id,
            "aud": "appstoreconnect-v1",
            "exp": now + ttl_seconds,
        },
        pem,
        algorithm="ES256",
        headers={"kid": key_id, "alg": "ES256"},
    )


def generate_apple_storekit_token(
    secret_b64: str,
    key_id: str,
    issuer_id: str,
    bundle_id: str,
    *,
    ttl_seconds: int = 3600,
    nonce: Optional[str] = None,
) -> str:
    """生成 StoreKit 2 API JWT（含 iat/nonce/bid）。"""
    pem = base64_to_pem(secret_b64)
    now = int(time.time())
    return jwt.encode(
        {
            "iss": issuer_id,
            "aud": "appstoreconnect-v1",
            "iat": now,
            "exp": now + ttl_seconds,
            "nonce": nonce or str(uuid.uuid4()),
            "bid": bundle_id,
        },
        pem,
        algorithm="ES256",
        headers={"alg": "ES256", "kid": key_id, "typ": "JWT"},
    )


def generate_apple_token_from_pem(
    pem_key: str,
    key_id: str,
    issuer_id: str,
    bundle_id: str,
    *,
    ttl_seconds: int = 3600,
    nonce: Optional[str] = None,
) -> str:
    """直接用 `.p8` 文件内容（PEM 字符串）生成与 `pay.py` 等价的 JWT。"""
    now = int(time.time())
    return jwt.encode(
        {
            "iss": issuer_id,
            "aud": "appstoreconnect-v1",
            "iat": now,
            "exp": now + ttl_seconds,
            "nonce": nonce or str(uuid.uuid4()),
            "bid": bundle_id,
        },
        pem_key,
        algorithm="ES256",
        headers={"alg": "ES256", "kid": key_id, "typ": "JWT"},
    )
