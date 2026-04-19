"""AES 加解密工具：

- `aes_cbc_encrypt/decrypt`：沿用历史实现（key 同时作 IV，hex 编码密文）。
- `aes_gcm_encrypt/decrypt`：对业务会话加解密，使用 `cryptography` 库。
- `hkdf_derive`：ECDH + HKDF 会话密钥派生。
"""
from __future__ import annotations

import base64
import os
from typing import Dict

from Crypto.Cipher import AES as PyCryptoAES
from Crypto.Util.Padding import pad, unpad
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

AES_KEY_SIZE = 32
GCM_IV_LENGTH = 12


def _to_hex(data: bytes) -> str:
    return "".join(f"{b:02x}" for b in data)


def aes_cbc_encrypt(key: str, message: str) -> str:
    """与 Java 侧实现对齐：key 字节同时作为 IV，返回 hex 密文。"""
    assert key and len(key) in (16, 24, 32), "Key 必须是 16/24/32 字节"
    key_bytes = key.encode("utf-8")
    cipher = PyCryptoAES.new(key_bytes, PyCryptoAES.MODE_CBC, iv=key_bytes)
    encrypted = cipher.encrypt(pad(message.encode("utf-8"), PyCryptoAES.block_size))
    return _to_hex(encrypted)


def aes_cbc_decrypt(key: str, hex_cipher: str) -> str:
    assert key and len(key) in (16, 24, 32), "Key 必须是 16/24/32 字节"
    key_bytes = key.encode("utf-8")
    cipher_bytes = bytes.fromhex(hex_cipher)
    cipher = PyCryptoAES.new(key_bytes, PyCryptoAES.MODE_CBC, iv=key_bytes)
    decrypted = unpad(cipher.decrypt(cipher_bytes), PyCryptoAES.block_size)
    return decrypted.decode("utf-8")


def hkdf_derive(shared_secret: bytes, salt: bytes, info: bytes, length: int = AES_KEY_SIZE) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=length, salt=salt, info=info).derive(shared_secret)


def aes_gcm_encrypt(plaintext: str, aes_key: bytes) -> Dict[str, str]:
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(GCM_IV_LENGTH)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return {
        "data": base64.b64encode(ct).decode(),
        "nonce": base64.b64encode(nonce).decode(),
    }


def aes_gcm_decrypt(enc_data: Dict[str, str], aes_key: bytes) -> str:
    aesgcm = AESGCM(aes_key)
    nonce = base64.b64decode(enc_data["nonce"])
    ct = base64.b64decode(enc_data["data"])
    return aesgcm.decrypt(nonce, ct, None).decode("utf-8")


class AESUtil:
    """历史 API 兼容壳：`AESUtil.encrypt/decrypt(key, msg)`。"""

    @staticmethod
    def encrypt(key: str, message: str) -> str:
        return aes_cbc_encrypt(key, message)

    @staticmethod
    def decrypt(key: str, hex_cipher: str) -> str:
        return aes_cbc_decrypt(key, hex_cipher)
