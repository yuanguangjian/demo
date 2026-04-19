import json
import time
import requests
import EccUtil


class ipc:

    def __init__(self, base):
        self.base = base
        self.headers = {
            "x-ugreen-app-system": "ios",
            "content-type": "application/json"
        }

    #   上报SN/密钥接口
    def snSubmit(self, data):
        path = "/metadata/v1/factory/snSubmit"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(reuslt.text)

    #   上报SN/密钥接口
    def snSubmitTest(self, data):
        path = "/metadata/v1/factory/snSubmitTest"
        url = self.base + path
        print(url)
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(reuslt.text)

    #   产测切换用户状态
    def switchState(self, data):
        path = "/metadata/v1/factory/switchState"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(reuslt.text)
    #   根据mac 地址获取sn
    def getSnByMac(self, mac,productModel):
        path = f"/metadata/v1/factory/getSn?mac={mac}&productModel={productModel}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(reuslt.text)

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
    sn = "I50000U58Q3000AA"
    productModel = "010004"
    nonce =int(time.time() * 1000)
    privateKey, publicKey = EccUtil.genKey()
    version = "1.0.0"
    key = {
        "privateKey": privateKey,
        "publicKey": publicKey,
        "version": version
    }
    saveSecret(sn, key)
    clientId = "HaxUIUiF1wVJXEK2OQGJHQ=="
    clientSecret = "MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCBWKiQrr6JWXCBcedM0BFD1OCdEhv+YPw3y0bbv05NY9g=="
    # base = "https://iot.ugreeniot.com"
    base = "http://localhost:9021"
    # base = "https://iot-test.ugreeniot.com"
    # base = "https://ces.ugreeniot.com"
    # base = "https://test2.ugreeniot.com"
    ipc = ipc(base)

    # 设备签名
    data = {
        "mac": sn,
        "nonce": nonce,
        "productModel": productModel,
        "publicKey": publicKey,
        "sn": sn,
        "version": version
    }
    sortData = EccUtil.ascii_sort(data)
    # 模拟设备签名
    sign = EccUtil.sign(sortData, privateKey)
    data["sign"] = sign
    # 添加工厂需要的参数
    data["clientId"] = clientId
    data["timestamp"] = nonce
    # 模拟工厂签名
    sortData = EccUtil.ascii_sort(data)
    clientSign = EccUtil.sign(sortData, clientSecret)

    data["clientSign"] = clientSign
    data = json.dumps(data)
    # print(data)
    # ipc.snSubmit(data)

    ipc.snSubmitTest(data)

    # ipc.switchState(data)
    # Camera001 I50001A5J6200039  010001 I50001A5J6200039
    # ipc.getSnByMac("I50000U58Q300098","010001")
