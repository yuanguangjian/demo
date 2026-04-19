"""ECC 签名 / ECDH+AES-GCM 加解密 演示（合并 `ipc项目/EccDemo.py` + `ipc项目/xxx.py`）。

实际算法都在 `common.crypto.ecc` / `common.signing.ecc_ugreen` 里。
这里用同一段 demo 验证：生成密钥 -> ASCII 排序签名 -> ECDH 协商密钥 -> AES-GCM 加解密。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import json

from common.crypto.ecc import (
    decrypt_with_ecdh,
    encrypt_with_ecdh,
    gen_key,
    sign as sign_ecdsa,
    verify_sign as verify_ecdsa,
)
from common.logger import get_logger
from common.signing.ecc_ugreen import ascii_sort

_logger = get_logger(__name__)


def run_demo() -> None:
    private_b64, public_b64 = gen_key()
    _logger.info("设备私钥: %s", private_b64)
    _logger.info("设备公钥: %s", public_b64)

    test_map = {
        "sn": "I50000U58Q200031",
        "version": "1.0.0",
        "productModel": "CAMERA001",
        "nonce": "1235345436456546546546",
    }
    ascii_string = ascii_sort(test_map)
    _logger.info("ASCII 排序签名字符串: %s", ascii_string)

    signature = sign_ecdsa(ascii_string, private_b64)
    _logger.info("签名: %s", signature)
    _logger.info("验签结果: %s", verify_ecdsa(ascii_string, signature, public_b64))

    temp_private_b64, temp_public_b64 = gen_key()
    _logger.info("服务端临时私钥: %s", temp_private_b64)
    _logger.info("服务端临时公钥: %s", temp_public_b64)

    enc = encrypt_with_ecdh(
        json.dumps(test_map), public_b64, temp_private_b64, temp_public_b64
    )
    _logger.info("加密数据: %s", enc)
    dec = decrypt_with_ecdh(enc, private_b64, public_b64, temp_public_b64)
    _logger.info("解密后: %s", dec)


if __name__ == "__main__":
    run_demo()
