import json

import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64


class UserInfo:

    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.refresh_token = None
        self.headers = {
            "Content-Type": "application/json"
        }

    # 获取sid 加密数据接口 返回sid,publickey
    def get_sid_info(self):
        path = "/app/v1/user/security/getSidInfo"
        url = self.base_url + path
        result = requests.post(url, headers=self.headers)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                return j["data"]["sid"], j["data"]["publicKey"]

    def encode_data(self, d, publicKey):
        MAX_ENCRYPT_BLOCK = 256
        # 将 Base64 编码的密钥解码
        key_bytes = base64.b64decode(publicKey)
        # 使用 RSA 密钥对进行解密/加密
        key = RSA.import_key(key_bytes)
        cipher = PKCS1_v1_5.new(key)
        json_str = json.dumps(d)
        data = json_str.encode('utf-8')
        input_len = len(data)
        encrypted_data = bytearray()
        off_set = 0
        # 分段加密
        while input_len - off_set > 0:
            # 如果数据长度大于最大加密块，则分段处理
            if input_len - off_set > MAX_ENCRYPT_BLOCK:
                encrypted_data.extend(cipher.encrypt(data[off_set: off_set + MAX_ENCRYPT_BLOCK]))
            else:
                encrypted_data.extend(cipher.encrypt(data[off_set:]))
            off_set += MAX_ENCRYPT_BLOCK
        return base64.b64encode(encrypted_data).decode('utf-8')

    # 数据加密使用
    def send_data(self, d, path):
        sid, publicKey = self.get_sid_info()
        url = self.base_url + path
        encode = self.encode_data(d, publicKey)
        param = {
            "sid": sid,
            "data": encode
        }
        self.headers["Authorization"] = self.token
        result = requests.post(url, json=param, headers=self.headers)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                return result
            else:
                return result

    # 邮箱密码登录
    def emailLogin(self, data):
        path = "/app/v1/user/login/emailPasswordLogin"
        result = self.send_data(data, path)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                data = j["data"]
                self.token = data["token"]
                self.refresh_token = data["refreshToken"]
                return self.token

    # 手机号密码登录
    def mobolePassowrdLogin(self, mobile):
        data = getKey(mobile)
        path = "/app/v1/user/login/mobilePasswordLogin"
        result = self.send_data(data, path)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                data = j["data"]
                self.token = data["token"]
                self.refresh_token = data["refreshToken"]
                token = {
                    "token": self.token,
                    "refresh_token": self.refresh_token,
                    "userInfo": data["userInfo"],
                }
                saveData(data["userInfo"]["userId"], token)

    # 手机号密码登录
    def mobolePassowrdLoginxx(self, account):
        path = "/app/v1/user/login/mobilePasswordLogin"
        result = self.send_data(account, path)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                data = j["data"]
                return data["token"]
        return None


def login(self, url):
    user = UserInfo(url)
    # 手机号密码登录：
    mobile = "15338849809"
    user.mobolePassowrdLogin(mobile)


def getKey(key):
    with open('account.json', 'r') as file:
        data = json.load(file)
    if key in data:
        return data[key]
    return None


def saveData(key, d):
    # 读取 JSON 文件
    with open('account.json', 'r') as file:
        data = json.load(file)
    # 修改现有的键值对（如果存在）
    if key in data:
        data[key] = d
    else:
        # 添加新的键值对
        data[key] = d
    # 写回文件
    with open('account.json', 'w') as file:
        json.dump(data, file, indent=4)  # indent=4 用于美化格式


if __name__ == '__main__':
    # baseUrl = "https://dev3.ugreeniot.com/"
    # baseUrl = "https://test2.ugreeniot.com/"
    baseUrl = "http://iot-test.ugreeniot.com"
    user = UserInfo(baseUrl)

    # 手机号密码登录：
    mobile = "15338849809"
    user.mobolePassowrdLogin(mobile)

    # 邮箱密码登录
    # email = "";
    # user.emailLogin(email)
