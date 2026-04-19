import request
import EccUtil
import time
import fileUtil

headers = {
    "content-type": "application/json",
}


class Factory():

    def __init__(self, env):
        self.env = env
        self.client = request.Client(env)

    # 获取 sn
    def getSN(self, mac, productModel):
        path = f"/metadata/v1/factory/getSn?mac={mac}&productModel={productModel}"
        return self.client.request("GET", path=path, headers=headers, data=None)

    # 模拟工厂上报
    def submitSnTest(self, sn, productModel):
        privateKey, publicKey = EccUtil.genKey()
        version = "1.0.0"
        value = {
            "privateKey": privateKey,
            "publicKey": publicKey,
            "version": version
        }
        data = {
            "mac": sn,
            "nonce": str(int(time.time() * 1000)),
            "productModel": productModel,
            "publicKey": publicKey,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        # 模拟设备签名
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        # 工厂签名
        self.factorySign(data)
        path = "/metadata/v1/factory/snSubmitTest"
        result = self.client.request("POST", path=path, headers=headers, data=data)
        if result["code"] == 100000:
            key = f"{productModel}_{sn}"
            fileUtil.saveSnSecret(key, value, self.env)
        return result["data"]

    # 直接上报
    def submitSn(self, sn, productModel):
        privateKey, publicKey = EccUtil.genKey()
        version = "1.0.0"
        value = {
            "privateKey": privateKey,
            "publicKey": publicKey,
            "version": version
        }
        data = {
            "mac": sn,
            "nonce": str(int(time.time() * 1000)),
            "productModel": productModel,
            "publicKey": publicKey,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        # 模拟设备签名
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        # 工厂签名
        self.factorySign(data)
        path = "/metadata/v1/factory/snSubmit"
        result = self.client.request("POST", path=path, headers=headers, data=data)
        if result["code"] == 100000:
            key = f"{productModel}_{sn}"
            fileUtil.saveSnSecret(key, value, self.env)
        return result["data"]

    # 切换状态
    def switchState(self, sn, productModel):
        snInfo = fileUtil.getSnSecret(productModel, sn, self.env)
        if snInfo:
            privateKey = snInfo["privateKey"]
            version = snInfo["version"]
            data = {
                "mac": sn,
                "nonce": str(int(time.time() * 1000)),
                "productModel": productModel,
                "sn": sn,
                "version": version
            }
            sortData = EccUtil.ascii_sort(data)
            # 模拟设备签名
            sign = EccUtil.sign(sortData, privateKey)
            data["sign"] = sign
            # 工厂签名
            self.factorySign(data)
            path = "/metadata/v1/factory/switchState"
            self.client.request("POST", path=path, headers=headers, data=data)
        else:
            print("密钥不存在")

    def factorySign(self, data):
        # 添加工厂需要的参数
        secret = fileUtil.openFile("factory.json")[self.env]
        data["clientId"] = secret["AppId"]
        data["timestamp"] = str(int(time.time() * 1000))
        # 模拟工厂签名
        sortData = EccUtil.ascii_sort(data)
        clientSign = EccUtil.sign(sortData, secret["AppSecret"])
        data["clientSign"] = clientSign


if __name__ == '__main__':
    factory = Factory("device")
    sn = "I50000U57Q200017"
    model = "00000"

    # data =factory.submitSnTest(sn, model)
    # factory.switchState(sn, model)
    # data =factory.submitSn(sn, model)
