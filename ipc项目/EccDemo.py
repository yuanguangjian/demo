import base64
import json
import os
from collections import OrderedDict
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 常量
EC_CURVE = ec.SECP256R1()
SIGNATURE_ALGORITHM = hashes.SHA256()
AES_KEY_SIZE = 32  # 256 bit
GCM_IV_LENGTH = 12
GCM_TAG_LENGTH = 16  # bytes


def generate_ec_keypair():
    private_key = ec.generate_private_key(EC_CURVE)
    public_key = private_key.public_key()
    return private_key, public_key

def key_to_base64(key, is_private=True):
    if is_private:
        b = key.private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())
    else:
        b = key.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo)
    return base64.b64encode(b).decode()

def base64_to_private_key(b64):
    der = base64.b64decode(b64)
    return serialization.load_der_private_key(der, password=None)

def base64_to_public_key(b64):
    der = base64.b64decode(b64)
    return serialization.load_der_public_key(der)

def ascii_sort(map_: dict):
    # 按key ASCII排序，非空value拼接key=value&，去掉最后&
    items = sorted((k, v) for k, v in map_.items() if v and str(v).strip() != "")
    return "&".join(f"{k}={v}" for k, v in items)

def sign(data: str, private_key_b64: str):
    private_key = base64_to_private_key(private_key_b64)
    signature = private_key.sign(data.encode('utf-8'), ec.ECDSA(SIGNATURE_ALGORITHM))
    # Java默认Base64是DER编码，python cryptography输出的也是DER
    return base64.b64encode(signature).decode()

def verify_sign(data: str, signature_b64: str, public_key_b64: str):
    public_key = base64_to_public_key(public_key_b64)
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(signature, data.encode('utf-8'), ec.ECDSA(SIGNATURE_ALGORITHM))
        return True
    except Exception as e:
        print("验签失败: ", e)
        return False

def hkdf_derive(shared_secret: bytes, salt: bytes, info: bytes, length: int):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        info=info
    )
    return hkdf.derive(shared_secret)

def encrypt_data(data: str, device_public_b64: str, server_temp_private_b64: str, server_temp_public_b64: str):
    # ECDH密钥协商
    device_public = base64_to_public_key(device_public_b64)
    server_temp_private = base64_to_private_key(server_temp_private_b64)
    shared_secret = server_temp_private.exchange(ec.ECDH(), device_public)
    # HKDF派生密钥（salt用服务端临时公钥，info用设备公钥）
    salt = base64.b64decode(server_temp_public_b64)
    info = base64.b64decode(device_public_b64)
    aes_key = hkdf_derive(shared_secret, salt, info, AES_KEY_SIZE)
    # AES-GCM加密
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(GCM_IV_LENGTH)
    ct = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
    return {
        "data": base64.b64encode(ct).decode(),
        "nonce": base64.b64encode(nonce).decode()
    }

def decrypt_data(enc_data: dict, device_private_b64: str, device_public_b64: str, server_temp_public_b64: str):
    # ECDH密钥协商
    server_temp_public = base64_to_public_key(server_temp_public_b64)
    device_private = base64_to_private_key(device_private_b64)
    shared_secret = device_private.exchange(ec.ECDH(), server_temp_public)
    # HKDF派生密钥（salt用服务端临时公钥，info用设备公钥）
    salt = base64.b64decode(server_temp_public_b64)
    info = base64.b64decode(device_public_b64)
    aes_key = hkdf_derive(shared_secret, salt, info, AES_KEY_SIZE)
    # AES-GCM解密
    aesgcm = AESGCM(aes_key)
    nonce = base64.b64decode(enc_data["nonce"])
    ct = base64.b64decode(enc_data["data"])
    decrypted = aesgcm.decrypt(nonce, ct, None)
    return decrypted.decode('utf-8')

if __name__ == "__main__":



    # 生成设备密钥对
    private_key, public_key = generate_ec_keypair()
    private_b64 = key_to_base64(private_key, True)
    public_b64 = key_to_base64(public_key, False)

    # private_b64 = "MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCA60xLh8m9/lj4HKbHnAH+ikvTMGoFHfPy4Vld5jNa/hA=="
    # public_key = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEfs/nAU9rHRurSbYSTLsRAvIp/Pm6jytphuA7rM4MHsLymX1IIq2arSFVujvdsfQ5NB1M8WV9EdHJ/LfQQNciXw=="

    print("设备私钥:", private_b64)
    print("设备公钥:", public_b64)

    # 测试签名与验签
    test_map = {
        "sn": "I50000U58Q200031",
        "version": "1.0.0",
        "productModel": "CAMERA001",
        "nonce": "1235345436456546546546"
    }
    ascii_string = ascii_sort(test_map)
    print("ASCII排序签名字符串:", ascii_string)
    signature = sign(ascii_string, private_b64)
    print("签名:", signature)
    print("验签结果:", verify_sign(ascii_string, signature, public_b64))

    # 服务端临时密钥对
    temp_private, temp_public = generate_ec_keypair()
    temp_private_b64 = key_to_base64(temp_private, True)
    temp_public_b64 = key_to_base64(temp_public, False)
    print("服务端临时私钥:", temp_private_b64)
    print("服务端临时公钥:", temp_public_b64)

    # 加密数据
    data_json = json.dumps(test_map)
    enc_data = encrypt_data(data_json, public_b64, temp_private_b64, temp_public_b64)
    print("加密数据:", enc_data)

    # 解密数据
    decrypted_json = decrypt_data(enc_data, private_b64, public_b64, temp_public_b64)
    print("解密后:", decrypted_json)

