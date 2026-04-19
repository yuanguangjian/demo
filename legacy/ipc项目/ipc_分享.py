import requests
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

base = ""
token = ""
app_user_id = ""


class ipc:

    def __init__(self, base, token):

        self.base = base
        self.headers = {
            "content-type": "application/json",
            "authorization": token,
            "app_user_id": app_user_id,
            "x-ugreen-app-system": "ios"
        }

    #   获取sid
    def getSidInfo(self):
        path = "/app/v1/user/security/getSidInfo"
        url = self.base + path
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
        json_str = d
        print(f"encodeData:{json_str}")
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

    #   校验账号
    def checkAccount(self, phone):
        data = {
            "sid": sid,
            "account": phone
        }
        data = json.dumps(data)
        path = "/app/v1/user/checkAccount"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("校验账号:" + reuslt.text)
        return reuslt.text

    #   校验账号
    def checkAccountRpc(self):
        data = {
            "sid": sid,
            "account": account
        }
        data = json.dumps(data)
        path = "/rpc/v1/user/checkAccount"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("校验账号checkAccountRpc:" + reuslt.text)

    #   查询账号信息
    def getUserInfo(self, userId):
        path = "/rpc/v1/user/getUserInfoByUserId?userId=" + str(userId)
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("查询账号信息:" + reuslt.text)

    # 生成二维码
    def qrCode(self):
        data = {
            "productSerialNo": productSerialNo,
            "deviceUniqueCode": deviceUniqueCode,
            "role": role,
            "permission": permission,
        }
        data = json.dumps(data)
        path = "app/v1/variety/share/qrCode"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("生成二维码:" + reuslt.text)

    # 获取二维码信息
    def qrCodeInfo(self):
        data = {
            "qrCode": qrCode,
            "productSerialNo": productSerialNo,
            "deviceUniqueCode": deviceUniqueCode,
        }
        data = json.dumps(data)
        path = "app/v1/variety/share/qrCodeInfo"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("获取二维码信息:" + reuslt.text)

    # 接收二维码分享
    def qrCodeReceive(self):
        data = {
            "qrCode": qrCode,
            "productSerialNo": productSerialNo,
            "deviceUniqueCode": deviceUniqueCode,
        }
        data = json.dumps(data)
        path = "app/v1/variety/share/qrCodeReceive"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("接收二维码分享:" + reuslt.text)

    # 创建账号分享
    def account(self, receiver):
        data = {
            "productSerialNo": productSerialNo,
            "deviceUniqueCode": deviceUniqueCode,
            "role": role,
            "permission": permission,
            "receiver": receiver,
        }
        data = json.dumps(data)
        path = "app/v1/variety/share/account"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("创建账号分享:" + reuslt.text)

    # 获取账号分享列表
    def homeList(self):
        path = "app/v1/variety/share/homeList"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("获取账号分享列表:" + reuslt.text)

    # 接收，拒绝，接口
    def receive(self):
        data = {
            "id": id,
            "shareStatus": shareStatus,
        }
        data = json.dumps(data)
        path = "app/v1/variety/share/receive"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("接收，拒绝，接口:" + reuslt.text)

    # 设备分享列表
    def shareList(self):
        path = f"app/v1/variety/share/shareList?deviceUniqueCode={deviceUniqueCode}&productSerialNo={productSerialNo}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("设备分享列表:" + reuslt.text)

    # 取消分享
    def cancel(self, id):
        path = f"app/v1/variety/share/cancel/{id}"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers)
        print("取消分享:" + reuslt.text)

    # 设备信息
    def deviceInfo(self):
        path = f"app/v1/variety/share/deviceInfo?deviceUniqueCode={deviceUniqueCode}&productSerialNo={productSerialNo}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("设备信息:" + reuslt.text)

    # 根据ID查询分享信息
    def deviceInfoById(self):
        path = f"app/v1/variety/share/deviceInfoById?id={id}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("根据ID查询分享信息:" + reuslt.text)

    # 固件检测升级
    def check_upgrade(self, data):
        path = f"/app/v1/software/version/check_upgrade"
        url = base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("固件检测升级:" + reuslt.text)

    # 查询消息
    def msg_list(self):
        path = f"/app/v1/variety/message/pagination?page=1&size=100"
        url = base + path
        reuslt = requests.get(url, headers=self.headers)
        print("查询消息:" + reuslt.text)


def getUserInfo(base, token, phone):
    i = ipc(base, token)
    return i.checkAccount(phone)


if __name__ == '__main__':
    # base = "https://iot-test.ugreeniot.com/"
    # base = "https://dev3.ugreeniot.com/"
    base = "http://127.0.0.1:9010/"
    token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjI4MjU3MjIsImV4cCI6MTc2Mjk0NTcyMn0.vmHgyk5fAuQePsKle_9lzrEcvlS3DtofeGuwnanKHp0"
    # token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxNTAyOTkyMyIsIlVTRVJfQ09VTlRSWV9DT0RFIjoiQ04iLCJqdGkiOiIxNTAyOTkyMyIsImlhdCI6MTc2MTkwMjg1MSwiZXhwIjoxNzYxOTA0MDUxfQ.SXmaOhk5Q7jsHo5CziDcDepbv_uQJSjG-ucQ5xCayaE"
    account = "13528786864"
    productSerialNo = "010004"
    deviceUniqueCode = "I50000U58Q3000AA"
    role = 1
    permission = "live,control"
    # 1314002  1314020
    app_user_id = "1314002"
    ipc = ipc(base, token)
    # 获取sid info 信息
    sid = ""
    # sid, publicKey = ipc.getSidInfo()
    # 加密数据
    # account = ipc.encode_data(account, publicKey)
    # 校验账号
    # ipc.checkAccount()
    # 获取用户信息
    # ipc.getUserInfo("1310008")

    #########################################  二维码分享 ##########################################
    # 创建二维码
    # ipc.qrCode()
    # 扫码
    qrCode = "17032364735488"
    # ipc.qrCodeInfo()

    # 接收分享
    # ipc.qrCodeReceive()

    # 设备分享列表
    # ipc.shareList()

    # 分享者主动取消分享
    id = "139"
    # ipc.cancel(id)
    # 分享设备详情
    # ipc.deviceInfo()
    # ipc.deviceInfoById()
    #########################################  账号分享  ##########################################

    # 创建账号分享
    receiver = "1314002"
    # ipc.account(receiver)
    # 首页列表
    # ipc.homeList()
    # 接受
    id = "149"
    shareStatus = 1
    # ipc.receive()

    # 消息查询分享详情
    # ipc.deviceInfoById()

    #########################################  用户消息列表  ##########################################

    # ipc.msg_list()

    #########################################  检测升级  ##########################################

    # 检测升级
    data = {
        "serialNo": "IPC_ID500",
        "versionCode": 0,
        "versionName": "IPC_ID500",
    }
    data = json.dumps(data)
    # ipc.check_upgrade(data)
