"""Apple JWT Token 管理器。

统一 App Store Connect / StoreKit 2 的令牌生成。底层复用 `common.signing.jwt_es256`。

原：`apple/appleToken.py`、`pay.py`。硬编码凭证保持原样。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from common.logger import get_logger
from common.signing.jwt_es256 import (
    generate_apple_connect_token,
    generate_apple_storekit_token,
    generate_apple_token_from_pem,
)

_logger = get_logger(__name__)


@dataclass
class AppleCredentials:
    store_connect_secret: str = (
        "MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgz1QzSdXO1Csts7kpO8t9uPEAzsKUVyIkDIenFfWakcygCgYIKoZIzj0DAQehRANCAAQ9ymS1gdx/ZCWdanktmNIfbmMnc1w4glqr30WJ6hSUpQB2SdyyzhDPwhQMarNryrrUHqM+CtN0ku8tPWW6a2nN"
    )
    store_connect_key_id: str = "CFX6WQ3G8M"
    issuer_id: str = "62225453-9d69-4a67-bb6d-33f35c74ead1"
    in_app_secret: str = (
        "MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgjgCv0sCfggrrpWbJ+o0+cluRS8Re60d4rHHqXBPRe2ygCgYIKoZIzj0DAQehRANCAAQKy9GUG72y772HzwPjV2OvGTx7Wmito7TIdNySViorwaOclB288G+jLjv24hYGtlzndgEKXx9BWGuOv4WerKF+"
    )
    in_app_key_id: str = "VQ79WJM6U4"
    bundle_id: str = "com.ugreen.iot"


class AppleToken:
    """对外暴露与原 `AppleToken` 同名的方法。"""

    def __init__(self, credentials: Optional[AppleCredentials] = None) -> None:
        self.credentials = credentials or AppleCredentials()

    def get_connect_token(self, *, ttl_seconds: int = 1200) -> str:
        return generate_apple_connect_token(
            self.credentials.store_connect_secret,
            self.credentials.store_connect_key_id,
            self.credentials.issuer_id,
            ttl_seconds=ttl_seconds,
        )

    def get_storekit_token(self, *, ttl_seconds: int = 3600, nonce: Optional[str] = None) -> str:
        return generate_apple_storekit_token(
            self.credentials.in_app_secret,
            self.credentials.in_app_key_id,
            self.credentials.issuer_id,
            self.credentials.bundle_id,
            ttl_seconds=ttl_seconds,
            nonce=nonce,
        )

    @classmethod
    def from_p8_file(
        cls,
        pem_path: str | Path,
        *,
        key_id: str,
        issuer_id: str,
        bundle_id: str,
        ttl_seconds: int = 3600,
    ) -> str:
        """从 `.p8` 文件读取 PEM 生成 StoreKit Token（原 `pay.py` 的流程）。"""
        pem = Path(pem_path).read_text(encoding="utf-8")
        return generate_apple_token_from_pem(
            pem, key_id=key_id, issuer_id=issuer_id, bundle_id=bundle_id, ttl_seconds=ttl_seconds
        )


if __name__ == "__main__":
    token = AppleToken()
    _logger.info("Connect Token: %s", token.get_connect_token())
    _logger.info("StoreKit Token: %s", token.get_storekit_token())
