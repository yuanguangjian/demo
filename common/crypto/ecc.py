"""ECC (SECP256R1) 工具：密钥生成 / Base64 互转 / ECDSA 签名验签 /
ECDH + HKDF + AES-GCM 会话加解密。

取自历史 `utils/EccUtil.py`，去除演示打印，统一异常抛出。
"""
from __future__ import annotations

import base64
from typing import Dict, Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from .aes import AES_KEY_SIZE, aes_gcm_decrypt, aes_gcm_encrypt, hkdf_derive

EC_CURVE = ec.SECP256R1()
SIGNATURE_ALGORITHM = hashes.SHA256()


def generate_ec_keypair() -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    private_key = ec.generate_private_key(EC_CURVE)
    return private_key, private_key.public_key()


def key_to_base64(key, is_private: bool = True) -> str:
    if is_private:
        der = key.private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    else:
        der = key.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    return base64.b64encode(der).decode()


def base64_to_private_key(b64: str) -> ec.EllipticCurvePrivateKey:
    return serialization.load_der_private_key(base64.b64decode(b64), password=None)


def base64_to_public_key(b64: str) -> ec.EllipticCurvePublicKey:
    return serialization.load_der_public_key(base64.b64decode(b64))


def gen_key() -> Tuple[str, str]:
    """生成一对 Base64 编码的 ECC 密钥。"""
    priv, pub = generate_ec_keypair()
    return key_to_base64(priv, True), key_to_base64(pub, False)


def sign(data: str, private_key_b64: str) -> str:
    """ECDSA(SHA-256) 签名，返回 Base64 DER 字符串。"""
    private_key = base64_to_private_key(private_key_b64)
    signature = private_key.sign(data.encode("utf-8"), ec.ECDSA(SIGNATURE_ALGORITHM))
    return base64.b64encode(signature).decode()


def verify_sign(data: str, signature_b64: str, public_key_b64: str) -> bool:
    try:
        public_key = base64_to_public_key(public_key_b64)
        public_key.verify(
            base64.b64decode(signature_b64),
            data.encode("utf-8"),
            ec.ECDSA(SIGNATURE_ALGORITHM),
        )
        return True
    except Exception:
        return False


def _derive_session_key(
    private_key_b64: str,
    peer_public_key_b64: str,
    salt_b64: str,
    info_b64: str,
) -> bytes:
    private_key = base64_to_private_key(private_key_b64)
    peer_public = base64_to_public_key(peer_public_key_b64)
    shared_secret = private_key.exchange(ec.ECDH(), peer_public)
    return hkdf_derive(
        shared_secret,
        salt=base64.b64decode(salt_b64),
        info=base64.b64decode(info_b64),
        length=AES_KEY_SIZE,
    )


def encrypt_with_ecdh(
    data: str,
    device_public_b64: str,
    server_temp_private_b64: str,
    server_temp_public_b64: str,
) -> Dict[str, str]:
    """服务端侧：用设备公钥 + 自己的临时密钥协商会话 key，然后 AES-GCM 加密。"""
    aes_key = _derive_session_key(
        server_temp_private_b64,
        device_public_b64,
        salt_b64=server_temp_public_b64,
        info_b64=device_public_b64,
    )
    return aes_gcm_encrypt(data, aes_key)


def decrypt_with_ecdh(
    enc_data: Dict[str, str],
    device_private_b64: str,
    device_public_b64: str,
    server_temp_public_b64: str,
) -> str:
    """设备侧：用自己的私钥 + 服务端临时公钥协商会话 key，然后 AES-GCM 解密。"""
    aes_key = _derive_session_key(
        device_private_b64,
        server_temp_public_b64,
        salt_b64=server_temp_public_b64,
        info_b64=device_public_b64,
    )
    return aes_gcm_decrypt(enc_data, aes_key)
