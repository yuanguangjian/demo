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
        # 确保使用 PKCS8 格式，DER 编码
        b = key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        # 使用 SubjectPublicKeyInfo 格式，DER 编码
        b = key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    return base64.b64encode(b).decode('ascii')


def base64_to_private_key(b64):
    # 确保输入是字符串格式
    if isinstance(b64, bytes):
        b64 = b64.decode('ascii')

    # 移除可能的空白字符
    b64 = b64.strip()

    try:
        der = base64.b64decode(b64)
        return serialization.load_der_private_key(der, password=None)
    except Exception as e:
        print(f"解析私钥失败: {e}")
        raise


def base64_to_public_key(b64):
    # 确保输入是字符串格式
    if isinstance(b64, bytes):
        b64 = b64.decode('ascii')

    # 移除可能的空白字符
    b64 = b64.strip()

    try:
        der = base64.b64decode(b64)
        return serialization.load_der_public_key(der)
    except Exception as e:
        print(f"解析公钥失败: {e}")
        raise


def ascii_sort(map_: dict):
    # 按key ASCII排序，非空value拼接key=value&，去掉最后&
    items = sorted((k, v) for k, v in map_.items() if v and str(v).strip() != "")
    return "&".join(f"{k}={v}" for k, v in items)


def sign(data: str, private_key_b64: str):
    private_key = base64_to_private_key(private_key_b64)
    signature = private_key.sign(data.encode('utf-8'), ec.ECDSA(SIGNATURE_ALGORITHM))
    # Java默认Base64是DER编码，python cryptography输出的也是DER
    return base64.b64encode(signature).decode('ascii')


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
        "data": base64.b64encode(ct).decode('ascii'),
        "nonce": base64.b64encode(nonce).decode('ascii')
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


def validate_key_format(private_key_b64: str):
    """验证私钥格式是否正确"""
    try:
        # 尝试解析私钥
        private_key = base64_to_private_key(private_key_b64)

        # 检查密钥类型和曲线
        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            return False, "不是椭圆曲线私钥"

        # 检查曲线类型
        if private_key.curve.name != 'secp256r1':
            return False, f"曲线类型不匹配: {private_key.curve.name}"

        # 重新编码验证
        reencoded = key_to_base64(private_key, True)
        if reencoded != private_key_b64:
            return False, "重新编码后不匹配"

        return True, "格式正确"
    except Exception as e:
        return False, f"验证失败: {e}"


if __name__ == "__main__":
    # 生成设备密钥对
    private_key, public_key = generate_ec_keypair()
    # private_b64 = key_to_base64(private_key, True)
    # public_b64 = key_to_base64(public_key, False)
    private_b64 = "MHcCAQEEIM2PyX9bfUrYE1R8hyd3dJRswd3OE1zIcREa9xOoRm1qoAoGCCqGSM49AwEHoUQDQgAEuSoHI+k9jDdaRnFaBe9drhUzStsFAbyDmU7BKyfYvcLc3gI9V++KoqtxRyBdjCjBRUTxwl+Zk7tJGJ1ViQ6g0g==";
    public_b64 = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEuSoHI+k9jDdaRnFaBe9drhUzStsFAbyDmU7BKyfYvcLc3gI9V++KoqtxRyBdjCjBRUTxwl+Zk7tJGJ1ViQ6g0g==";


    print("设备私钥:", private_b64)
    print("设备公钥:", public_b64)

    # 验证私钥格式
    is_valid, message = validate_key_format(private_b64)
    print(f"私钥格式验证: {is_valid}, {message}")

    # 打印私钥的详细信息
    print(f"私钥长度: {len(private_b64)} 字符")
    print(f"私钥前50字符: {private_b64[:50]}...")

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