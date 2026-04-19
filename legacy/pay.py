# coding=UTF-8

import jwt
import time

# 读取密钥文件证书内容
f = open("D:\Downloads\SubscriptionKey_VQ79WJM6U4.p8")
key_data = f.read()
f.close()

# JWT Header

header = {
    "alg": "ES256", # 加密算法，默认值：ES256
    "kid": "VQ79WJM6U4", # 秘钥ID,需在App Store Connect生成
    "typ": "JWT" # 令牌类型，默认值：JWT
}

# JWT Payload
payload = {
    "iss": "62225453-9d69-4a67-bb6d-33f35c74ead1", # issuer ID,需在App Store Connect生成
    "aud": "appstoreconnect-v1", # 受众，固定值appstoreconnect-v1
    "iat": int(time.time()), # 发布时间
    "exp": int(time.time()) + 60 * 60, # 到期时间，60 minutes timestamp
    "nonce": "6edffe66-b482-11eb-8529-0242ac130003", # 唯一标识符
    "bid": "com.ugreen.iot" # Bundle ID
}

# JWT token
token = jwt.encode(headers=header, payload=payload, key=key_data, algorithm="ES256")

print("JWT Token:", token)
