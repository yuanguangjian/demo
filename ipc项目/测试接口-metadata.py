import json
import time
import requests
import EccUtil


class ipc:

    def __init__(self, base):
        self.base = base
        self.headers = {
            "content-type": "application/json"
        }

    #   上报SN/密钥接口
    def snSubmit(self, data):
        path = "/metadata/v1/factory/snSubmit"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
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
    sn = "I50000U57Q1100P2"
    productModel = "010001"
    nonce =int(time.time() * 1000)
    privateKey, publicKey = EccUtil.genKey()
    version = "1.0.0"
    key = {
        "privateKey": privateKey,
        "publicKey": publicKey,
        "version": version
    }
    clientId = "/UqvcYdkFJA1RIajPWEy9Q=="
    clientSecret = "MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCAMTGHKSzp/VIEZ608mGHgNlw4fOuVA6ia3yXUmN1x0Tg=="
    # base = "https://dev3.ugreeniot.com"
    base = "https://iot-test.ugreeniot.com"
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
    print(data)
    ipc.snSubmit(data)
    saveSecret(sn, key)
