import json

import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

from firebase_admin.credentials import RefreshToken


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
        print(f"请求url:{url} 结果是：{result.text}")
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
        print(f"json_str:{json_str}")
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
        print(f"加密的数据是：{encode}")
        param = {
            "sid": sid,
            "data": encode
        }
        self.headers["Authorization"] = self.token
        result = requests.post(url, json=param, headers=self.headers)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                print(f"请求地址：{url} 参数是：{param} 返回结果是：{result}")
                return result
            else:
                print(f"请求地址：{url} 参数是：{param} 发生了错误：{result.text}")
                return result

    # 邮箱注册发送验证码
    def register_sendEmailCode(self, email):
        path = "/app/v1/user/register/sendEmailCode"
        data = {
            "email": email,
        }
        self.send_data(data, path)

    # 邮箱注册
    def emailRegister(self, data):
        path = "/app/v1/user/register/emailRegister"
        result = self.send_data(data, path)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                data = j["data"]
                self.token = data["token"]
                self.refresh_token = j["refreshToken"]

    # 邮箱密码登录
    def emailLogin(self, data):
        path = "/app/v1/user/login/emailPasswordLogin"
        result = self.send_data(data, path)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                data = j["data"]
                self.token = data["token"]
                print(self.token)
                self.refresh_token = data["refreshToken"]

    # 手机号注册：发送验证码
    def mobile_register_send_code(self, mobile):
        path = "/app/v1/user/register/sendMobileCode"
        data = {
            "mobile": mobile
        }
        self.send_data(data, path)

    # 手机号注册
    def mobile_register(self, data):
        path = "/app/v1/user/register/mobileRegister"
        result = self.send_data(data, path)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                data = j["data"]
                self.token = data["token"]
                self.refresh_token = j["refreshToken"]

    # 手机号密码登录
    def mobolePassowrdLogin(self, data):
        path = "/app/v1/user/login/mobilePasswordLogin"
        result = self.send_data(data, path)
        if result.status_code == 200:
            j = result.json()
            if j["code"] == 100000:
                data = j["data"]
                print(data)
                self.token = data["token"]
                self.refresh_token = data["refreshToken"]
                print("token:", self.token)
                print("refresh_token:", self.refresh_token)

    def findPasswordByMobleSendCode(self, mobile):
        path = "/app/v1/user/safe/findPwdSendMobileCode"
        data = {
            "mobile": mobile
        }
        self.send_data(data, path)

    def findPasswordByMobile(self, data):
        path = "/app/v1/user/safe/mobileFindPassword"
        self.send_data(data, path)

    # 获取用户信息
    def get_user_info(self):
        path = "/app/v1/user/getUserInfo"
        result = self.send_data(d="hello", path=path)
        print(result.text)

    def findEmailPasswordSendCode(self, email):
        path = "/app/v1/user/safe/findPwdSendMailCode"
        data = {
            "email": email
        }
        self.send_data(data, path)

    def findEmailPassword(self, data):
        path = "/app/v1/user/safe/mailFindPassword"
        result = self.send_data(data, path)
        print(result)

    def mobileCodeLoginSend(self,data):
        path = "/app/v1/user/login/loginSendMobileCode"
        result = self.send_data(data, path)
        print(result)
    def mobileCodeLogin(self,data):
        path = "/app/v1/user/login/mobileCodeLogin"
        result = self.send_data(data, path)
        print(result)
    def emailCodeLoginSend(self,data):
        path = "/app/v1/user/login/emailCodeLoginSendMailCode"
        result = self.send_data(data, path)
        print(result)
    def emailCodeLogin(self,data):
        path = "/app/v1/user/login/emailCodeLogin"
        result = self.send_data(data, path)
        print(result)

if __name__ == '__main__':
    baseUrl = "https://ces.ugreeniot.com/"
    user = UserInfo(baseUrl)

    # 邮箱注册发送验证码
    # user.register_sendEmailCode("1007503475@qq.com")
    # 邮箱注册
    emailRegister_data = {
        "countryCode": "US",
        "email": "1007503475@qq.com",
        "emailCode": "902742",
        "password": "Aa123456"
    }
    # user.emailRegister(emailRegister_data)

    # 邮箱密码登录
    login_data = {
        "email": "1007503475@qq.com",
        "password": "Aa123456",
        "destroyFlag": 0
    }
    user.emailLogin(login_data)

    # 手机号注册：发送验证密码
    # user.mobile_register_send_code("15999621670")

    # 手机号注册：
    mobile_register_data = {
        "countryCode": "zh",
        "mobile": "15338849809",
        "mobileCode": "568120",
        "password": "Aa1234567",

    }
    # user.mobile_register(data=mobile_register_data)

    # 手机号密码登录：
    mobile_login = {
        "mobile": "15338849809",
        "password": "Aa123456",
        "destroyFlag": 0
    }
    # user.mobolePassowrdLogin(mobile_login)

    # 手机号 找回密码发送短信：
    # user.findPasswordByMobleSendCode("15338849801")

    findpasswordMobile = {
        "mobile": "15338849801",
        "mobileCode": "567284",
        "password": "Aa123456",
    }

    # 手机号找回密码：
    # user.findPasswordByMobile(findpasswordMobile)

    # 邮箱找回密码 发送验证码
    # user.findEmailPasswordSendCode("100750@qq.com")

    # 邮箱找回密码：
    # findEmailPassword_data = {
    #     "email": "100750@qq.com",
    #     "emailCode": "662015",
    #     "password": "Aa123457",
    # }
    # user.findEmailPassword(findEmailPassword_data)

    # login_sendMobile = {
    #     "mobile": "15338849809"
    # }
    # user.mobileCodeLoginSend(login_sendMobile)
    # login_data = {
    #     "mobile": "15338849809",
    #     "mobileCode": "567284"
    # }
    # user.mobileCodeLogin(login_data)

    # 获取用户信息
    # user.get_user_info()
