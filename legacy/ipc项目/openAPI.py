import json

import requests
import EccUtil
import time, sys
import urllib.parse

sn = ""
mac = sn
productModel = ""
deviceType = ""
userId = ""
app_system = ""
token = ""
base = ""


class ipc:

    def __init__(self, base, userId, token):
        self.base = base
        self.headers = {
            "authorization": token,
            "x-ugreen-app-system": app_system,
            "content-type": "application/json",
            "app_user_id": userId,
            "countryCode": "CN",
            "language": "zh-Hans",
        }

    # 获取app 信息
    def getAppInfo(self, platform):
        path = "/app/v1/variety/getAppInfo?platform=" + platform
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(f"获取app 信息", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   sn 检测
    def checkSN(self):
        data = {
            "productModel": productModel,
            "sn": sn,
            "deviceType": deviceType,
        }
        data = json.dumps(data)
        path = "/api/v1/meta/checkSn"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"sn 检测", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   获取三元组
    def getMeta(self, privateKey, version):
        data = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": productModel,
            "sn": sn,
            "version": version
        }

        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        data["deviceType"] = deviceType
        data["productSerialNo"] = productModel
        data = json.dumps(data)

        path = "/api/v1/meta/getMeta"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"获取三元组", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   校验签名
    def checkSign(self, privateKey, version):
        data = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": productModel,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        data = json.dumps(data)

        path = "/api/v1/meta/checkSign"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"校验签名", reuslt.text)
        return json.loads(reuslt.text)["data"]
    #   获取密钥
    def getSecret(self, privateKey, version):
        data = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": productModel,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        data = json.dumps(data)

        path = "/api/v1/meta/getSnSecret"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"获取密钥", reuslt.text)
        return json.loads(reuslt.text)["data"]
    #   更新设备密钥
    def updateSnSecret(self, data):
        path = "/app/v1/variety/updateSnSecret"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"更新设备密钥", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   修改设备名称
    def updateDeviceInfo(self, name):
        data = {
            "deviceName": name,
            "deviceUniqueCode": sn,
            "productSerialNo": productModel
        }

        data = json.dumps(data)

        path = "/app/v1/variety/updateDeviceInfo"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"修改设备名称", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   获取设备列表
    def deviceList(self):
        path = "/app/v1/variety/deviceList"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(f"获取设备列表", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   解绑接口
    def unbind(self):
        data = {
            "deviceType": deviceType,
            "sn": sn,
            "extra": {},
            "productModel": productModel
        }

        data = json.dumps(data)

        path = "/app/v1/variety/unbind"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"解绑接口", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   绑定接口
    def bind(self, privateKey, version):
        signData = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": productModel,
            "sn": sn,
            "version": version
        }

        sortData = EccUtil.ascii_sort(signData)
        sign = EccUtil.sign(sortData, privateKey)
        signData["sign"] = sign

        data = {
            "deviceMac": mac,
            "deviceType": deviceType,
            "deviceUniqueCode": sn,
            "productSerialNo": productModel,
            "extra": signData,
        }

        data = json.dumps(data)

        path = "/app/v1/variety/bind"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"绑定接口", reuslt.text)
        return json.loads(reuslt.text)["data"]

    # 获取bandToken接口
    def getBindToken(self):
        path = "/app/v1/variety/getBindToken"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(f"获取bandToken接口", reuslt.text)
        return json.loads(reuslt.text)["data"]

    def bindByToken(self, privateKey, version, bindToken):
        data = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": productModel,
            "sn": sn,
            "version": version
        }

        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        data["bindToken"] = bindToken
        data = json.dumps(data)

        path = "/app/v1/variety/bindByToken"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"调用bindToken接口", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   上报SN/密钥接口
    def snSubmitTest(self, version):
        privateKey, publicKey = EccUtil.genKey()
        key = {
            "privateKey": privateKey,
            "publicKey": publicKey,
            "version": version
        }
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": productModel,
            "publicKey": publicKey,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        data["clientSign"] = sign
        data["clientId"] = "xxxx"
        data["timestamp"] = int(time.time() * 1000)
        data = json.dumps(data)

        path = "/metadata/v1/factory/snSubmitTest"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"上报SN/密钥接口", reuslt.text)
        saveSecret(sn, key)
        return json.loads(reuslt.text)["data"]

    #   获取登录授权码
    def getAuthCode(self, client_id):
        data = {
            "client_id": client_id,
            "response_type": "code",
            "state": str(int(time.time() * 1000))
        }
        data = json.dumps(data)

        path = "/app/v1/oauth/authorize"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"获取登录授权码", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   获取绑定信息
    def getBindInfo(self):
        data = {
            "sn": sn,
            "productSerialNo": productModel
        }
        data = json.dumps(data)

        path = "/app/v1/variety/getBindInfo"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"获取绑定信息", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   根据bindToken查询绑定结果
    def getBindTokenResult(self, token):
        token = urllib.parse.quote(token)
        path = "/app/v1/variety/getBindTokenResult?bindToken=" + token
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(f"根据bindToken查询绑定结果", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   设备直接更新密钥
    def updateSnSecretDevice(self, privateKey, version, version_new):
        privateKey_new, publicKey_new = EccUtil.genKey()
        key = {
            "privateKey": privateKey_new,
            "publicKey": publicKey_new,
            "version": version_new
        }

        data = {
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "productModel": productModel,
            "sn": sn,
            "version": version_new,
            "oldVersion": version,
            "publicKey": publicKey_new
        }

        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        data = json.dumps(data)

        path = "/api/v1/meta/updateSnSecret"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"设备直接更新密钥", reuslt.text)
        saveSecret(sn, key)
        return json.loads(reuslt.text)["data"]


def getKey(sn):
    with open('key.json', 'r') as file:
        data = json.load(file)
    if sn in data:
        return data[sn]["privateKey"], data[sn]["publicKey"], data[sn]["version"]
    return None


def saveSecret(key, d):
    # 读取 JSON 文件
    with open('key.json', 'r') as file:
        data = json.load(file)

    # 修改现有的键值对（如果存在）
    if key in data:
        data[key] = d
    else:
        # 添加新的键值对
        data[key] = d
    # 写回文件
    with open('key.json', 'w') as file:
        json.dump(data, file, indent=4)  # indent=4 用于美化格式


if __name__ == '__main__':

    sn = "I50000U58Q300098"
    mac = sn
    productModel = "Camera001"
    deviceType = "ipc_camera"
    userId = "1268000"
    app_system = "ios"
    # token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxNTAyNjMwMCIsIlVTRVJfQ09VTlRSWV9DT0RFIjoiQ04iLCJqdGkiOiIxNTAyNjMwMCIsImlhdCI6MTc2MTkwMjY0MSwiZXhwIjoxNzYxOTAzODQxfQ.lhhSaQBPcUu_EuReOkMtcz4BgELBm6ZnBsITQhc3_6s"
    token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjI4NjEzNTYsImV4cCI6MTc2Mjk4MTM1Nn0.DNgDAu56NV8-BZnGh-R_A9vtmDjXsSY9_4N3WU6s3oA"
    # base = "https://dev3.ugreeniot.com"
    # base = "https://iot-test.ugreeniot.com"
    # base = "https://test2.ugreeniot.com"
    # base = "http://localhost:9010"
    base = "http://localhost:9023"

    ipc = ipc(base, userId, token)

    if not getKey(sn):
        print(f"sn:{sn} 公私钥不存在")
        version = "1.0.0"
        ipc.snSubmitTest(version)
    privateKey, publicKey, version = getKey(sn)
    print(f"sn:{sn}：私钥privateKey:{privateKey}")
    print(f"sn:{sn}：公钥publicKey:{publicKey}")
    print(f"sn:{sn}：版本version:{version}")


    # 校验SN
    # ipc.checkSN()
    # 获取三元组
    # ipc.getMeta(privateKey, version)

    # 校验签名
    # ipc.checkSign(privateKey, version)

    # 更新设备密钥
    version_new = "1.0.2"
    # ipc.updateSnSecretDevice(privateKey, version,version_new)

    #获取密钥
    # ipc.getSecret(privateKey, version)


