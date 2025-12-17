import json

import request
import EccUtil
import fileUtil
import time
import requests

privateKey = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgOBtWRkzFaNEvznFjQw/zySoehcna+UkdUgIr4SEqGWqhRANCAARYlrMpoIEY63nqnHr+C7bZcN3qTy//DfkFsHzwEu8UXaRt37sACnT/vz5PC36nmavYbXPUrSB83E2fJGK32Cse"
publicKey = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEWJazKaCBGOt56px6/gu22XDd6k8v/w35BbB88BLvFF2kbd+7AAp0/78+Twt+p5mr2G1z1K0gfNxNnyRit9grHg=="


class Consumer:
    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "x-ugreen-app-system": "ios",
            "content-type": "application/json",
            "countryCode": "CN",
            "language": "zh-Hans",
        }

    # 校验SN
    def checkSn(self, sn, model):
        data = {'sn': sn, 'productSerialNo': model}
        path = "/app/v1/variety/checkSn"
        return self.client.request(method="post", path=path, data=data, headers=self.headers)

    def getMeta(self, sn, model):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getMeta密钥不存在")
            return
        privateKey = snInfo["privateKey"]
        version = snInfo["version"]
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productSerialNo": model,
            "deviceType":"card",
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        path = "/app/v1/variety/getMeta"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    def chckSign(self, sn, model):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getMeta密钥不存在")
            return
        privateKey = snInfo["privateKey"]
        version = snInfo["version"]
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        path = "/app/v1/variety/checkSign"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    def getSnSecret(self, sn, model):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getMeta密钥不存在")
            return
        privateKey = snInfo["privateKey"]
        version = snInfo["version"]
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        path = "/app/v1/variety/getSnSecret"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    def updateSnSecret(self, sn, model):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getMeta密钥不存在")
            return
        privateKey = snInfo["privateKey"]
        version = snInfo["version"]
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "oldVersion": version
        }
        privateKey_new, publicKey_new = EccUtil.genKey()
        version_new = "1.0.1"
        data["publicKey"] = publicKey_new
        data["version"] = version_new
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        path = "/app/v1/variety/updateSnSecret"
        result = self.client.request(method="post", path=path, headers=self.headers, data=data)
        if result["code"] == 100000:
            key = f"{model}_{sn}"
            value = {
                "privateKey": privateKey_new,
                "publicKey": publicKey_new,
                "version": version_new
            }
            fileUtil.saveSnSecret(key, value, self.env)

    def switchState(self, sn, model):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getMeta密钥不存在")
            return
        privateKey = snInfo["privateKey"]
        version = snInfo["version"]
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign

        # 添加工厂需要的参数
        secret = fileUtil.openFile("factory.json")["dev"]
        data["clientId"] = secret["AppId"]
        data["timestamp"] = str(int(time.time() * 1000))
        # 模拟工厂签名
        sortData = EccUtil.ascii_sort(data)
        clientSign = EccUtil.sign(sortData, secret["AppSecret"])
        data["clientSign"] = clientSign

        path = "http://localhost:9021/metadata/v1/factory/switchState"
        print(time.time())
        xx = requests.post(url=path, headers=self.headers, data=json.dumps(data))
        print(time.time())
        print(xx.text)


if __name__ == '__main__':
    sn = "I50000U57Q200017"
    model = "00000"

    con = Consumer("device")

    # con.checkSn(sn, model)

    # con.getMeta(sn, model)

    # con.chckSign(sn, model)

    # con.getSnSecret(sn, model)

    con.updateSnSecret(sn, model)

    # con.switchState(sn, model)
