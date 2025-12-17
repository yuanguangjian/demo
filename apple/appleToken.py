import time
import uuid
import jwt


# 模拟配置类

class AppleToken:
    def __init__(self):
        self.store_connect_secret = "MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgz1QzSdXO1Csts7kpO8t9uPEAzsKUVyIkDIenFfWakcygCgYIKoZIzj0DAQehRANCAAQ9ymS1gdx/ZCWdanktmNIfbmMnc1w4glqr30WJ6hSUpQB2SdyyzhDPwhQMarNryrrUHqM+CtN0ku8tPWW6a2nN"
        self.store_connect_key_id = "CFX6WQ3G8M"
        self.issuer_id = "62225453-9d69-4a67-bb6d-33f35c74ead1"
        self.in_app_secret = "MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgjgCv0sCfggrrpWbJ+o0+cluRS8Re60d4rHHqXBPRe2ygCgYIKoZIzj0DAQehRANCAAQKy9GUG72y772HzwPjV2OvGTx7Wmito7TIdNySViorwaOclB288G+jLjv24hYGtlzndgEKXx9BWGuOv4WerKF+"
        self.in_app_key_id = "VQ79WJM6U4"
        self.bundle_id = "com.ugreen.iot"
        self.in_app_token_expires = 3600  # 秒，通常1小时

    def to_pem(self, base64_key: str) -> str:
        # 每64字符换行，符合PEM规范
        chunks = [base64_key[i:i + 64] for i in range(0, len(base64_key), 64)]
        body = "\n".join(chunks)
        return f"-----BEGIN PRIVATE KEY-----\n{body}\n-----END PRIVATE KEY-----\n"

    def get_connect_token(self):
        pem_key = self.to_pem(self.store_connect_secret)

        now = int(time.time())
        exp = now + 1200  # 20分钟

        headers = {
            "kid": self.store_connect_key_id,
            "alg": "ES256"
        }
        payload = {
            "iss": self.issuer_id,
            "aud": "appstoreconnect-v1",
            "exp": exp
        }
        token = jwt.encode(payload, pem_key, algorithm="ES256", headers=headers)
        return token

    def get_storekit_token(self):
        pem_key = self.to_pem(self.in_app_secret)

        now = int(time.time())
        exp = now + self.in_app_token_expires

        headers = {
            "alg": "ES256",
            "kid": self.in_app_key_id,
            "typ": "JWT"
        }
        payload = {
            "iss": self.issuer_id,
            "aud": "appstoreconnect-v1",
            "iat": now,
            "exp": exp,
            "nonce": str(uuid.uuid4()),
            "bid": self.bundle_id
        }
        token = jwt.encode(payload, pem_key, algorithm="ES256", headers=headers)
        return token


if __name__ == "__main__":
    token = AppleToken()
    print(token.get_connect_token())
    print(token.get_storekit_token())
