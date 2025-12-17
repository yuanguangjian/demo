import json

import requests
import EccUtil
import time, sys

sn = ""
mac = sn
productModel = ""
deviceType = ""
userId = ""
app_system = ""
token = ""
base = ""

class ipc:

    def __init__(self, base, token):
        self.base = base
        self.headers = {
            "authorization": token,
            "x-ugreen-app-system": app_system,
            "content-type": "application/json",
        }

    #   更新设备密钥
    def updateSnSecret(self, data):

        path = "/app/v1/variety/updateSnSecret"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"更新设备密钥", reuslt.text)
        return json.loads(reuslt.text)["data"]

    # 获取bandToken接口
    def getBindToken(self):
        path = "/app/v1/variety/getBindToken"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(f"获取bandToken接口", reuslt.text)
        return json.loads(reuslt.text)["data"]

    def bindByToken(self, data):
        path = "/app/v1/variety/bindByToken"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"绑定接口", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   上报SN/密钥接口
    def snSubmitTest(self, data):

        privateKey, publicKey = EccUtil.genKey()
        version = "1.0.0"
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
        # 上报密钥
        data = ipc.snSubmitTest(data)

        path = "/metadata/v1/factory/snSubmitTest"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(reuslt.text)


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

    sn = "I50000U57Q200005"
    mac = sn
    productModel = "Camera001"
    deviceType = "ipc_camera"
    base = "https://dev3.ugreeniot.com"
    token = ""

    ipc = ipc(base, token)

    if not getKey(sn):
        print(f"sn:{sn} 公私钥不存在 上报密钥")

        print(data)
        saveSecret(sn, key)


    privateKey, publicKey, version = getKey(sn)
    print(f"sn:{sn}")
    print(f"私钥privateKey:{privateKey}")
    print(f"公钥publicKey:{publicKey}")
    print(f"版本version:{version}")


    bindToken = "lYjJB3eDJHgDfXngxZl/WA=="
    # 获取绑定token 接口
    # bindToken = ipc.getBindToken()["bindToken"]

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

    # 测试 绑定接口
    ipc.bindByToken(data)



    # 更新密钥
    privateKey_new, publicKey_new = EccUtil.genKey()
    version_new = "1.0.1"
    key = {
        "privateKey": privateKey,
        "publicKey": publicKey,
        "version": version
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
    # 测试更新密钥接口
    ipc.updateSnSecret(data)
    # saveSecret(sn, key)
