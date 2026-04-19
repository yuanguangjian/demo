import base64
import jwt
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def generate_token(base64_private_key: str) -> str:
    # 1. Base64 解码
    key_bytes = base64.b64decode(base64_private_key)

    # 2. 加载 EC 私钥对象
    private_key = serialization.load_der_private_key(
        key_bytes,
        password=None,
        backend=default_backend()
    )

    # 3. 构造 payload
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    payload = {
        "sub": "ugreen-sign",
        "iss": "ugreen-service",
        "exp": exp_time
    }

    # 4. 生成 JWT (ES256)
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256"
    )
    return token


if __name__ == "__main__":
    # 假设你有一个 Base64 编码的私钥字符串
    base64_key = "MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCABytI6RcuA8rqPnkBOqtjmsTk0vL1oPE1jAT/8DO2/ew=="  # 示例
    token = generate_token(base64_key)
    print("JWT:", token)
