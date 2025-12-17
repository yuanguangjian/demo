import request
import time
import fileUtil
import EccUtil
import urllib


class Bind:
    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "x-ugreen-app-system": "IoS",
            "content-type": "application/json",
            "countryCode": "CN",
            "language": "zh-Hans",
            "app_user_id":"1326011"
        }

    # 获取app 信息
    def getAppInfo(self):
        data = {}
        path = "/app/v1/variety/getAppInfo?platform=rtcx"
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    #   sn 检测
    def checkSN(self, sn, model):
        data = {
            "productSerialNo": model,
            "sn": sn,
        }
        path = "/app/v1/variety/checkSn"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    def getBindInfo(self,sn,model):
        data = {
            "productSerialNo": model,
            "sn": sn,
        }
        path = "/app/v1/variety/getBindInfo"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    #   获取三元组
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
            "productModel": model,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        data["deviceType"] = "ipc_camera"
        data["productSerialNo"] = model
        path = "/app/v1/variety/getMeta"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    #   校验签名
    def checkSign(self, sn, model):
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

    #   修改设备名称
    def updateDeviceInfo(self, name, sn, model):
        data = {
            "deviceName": name,
            "deviceUniqueCode": sn,
            "productSerialNo": model
        }
        path = "/app/v1/variety/updateDeviceInfo"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    #   获取设备列表
    def deviceList(self):
        data = {}
        path = "/app/v1/variety/deviceList"
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    #   解绑接口
    def unbind(self, sn, model):
        data = {
            "deviceType": "ipc_camera",
            "deviceUniqueCode": sn,
            "extra": {},
            "productSerialNo": model
        }

        path = "/app/v1/variety/unbind"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    #   绑定接口
    def bind(self, sn, model):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getMeta密钥不存在")
            return
        privateKey = snInfo["privateKey"]
        version = snInfo["version"]
        signData = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": version
        }
        sortData = EccUtil.ascii_sort(signData)
        sign = EccUtil.sign(sortData, privateKey)
        signData["sign"] = sign
        data = {
            "deviceMac": sn,
            "deviceType": "ipc_camera",
            "deviceUniqueCode": sn,
            "productSerialNo": model,
            "extra": signData,
        }
        path = "/app/v1/variety/bind"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    # 获取bandToken接口
    def getBindToken(self):
        data = {}
        path = "/app/v1/variety/getBindToken"
        result = self.client.request(method="get", path=path, headers=self.headers, data=data)
        return result["data"]["bindToken"]

    def bindByToken(self, sn, model, bindToken):
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
        data["bindToken"] = bindToken

        path = "/app/v1/variety/bindByToken"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    #   获取绑定信息
    def getBindInfo(self, sn, model):
        data = {
            "sn": sn,
            "productSerialNo": model
        }
        path = "/app/v1/variety/getBindInfo"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    #   根据bindToken查询绑定结果
    def getBindTokenResult(self, token):
        data = {}
        token = urllib.parse.quote(token)
        path = "/app/v1/variety/getBindTokenResult?bindToken=" + token
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    #   更新设备密钥
    def updateSnSecret(self, sn, model, version_new):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getMeta密钥不存在")
            return
        privateKey = snInfo["privateKey"]
        version = snInfo["version"]
        privateKey_new, publicKey_new = EccUtil.genKey()
        value = {
            "privateKey": privateKey_new,
            "publicKey": publicKey_new,
            "version": version_new
        }
        data = {
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "productModel": model,
            "sn": sn,
            "version": version_new,
            "oldVersion": version,
            "publicKey": publicKey_new
        }

        sortData = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sortData, privateKey)
        data["sign"] = sign
        path = "/app/v1/variety/updateSnSecret"
        result = self.client.request(method="post", path=path, headers=self.headers, data=data)
        if result["code"] == 100000:
            key = f"{model}_{sn}"
            fileUtil.saveSnSecret(key, value, self.env)


if __name__ == '__main__':
    ipc = Bind("local")
    # ipc.getAppInfo()

    sn = "I50000U57Q200017"
    model = "00000"

    # ipc.checkSN(sn, model)

    # ipc.getBindInfo(sn,model)

    # ipc.getMeta(sn, model)

    # ipc.checkSign(sn, model)

    # ipc.unbind(sn, model)

    # ipc.bind(sn, model)

    ipc.unbind(sn, model)

    # ipc.deviceList()
    #
    # bindToken = ipc.getBindToken()
    # print(bindToken)
    # ipc.bindByToken(sn, model, bindToken)
    # ipc.getBindTokenResult(bindToken)
    #
    # ipc.deviceList()

    version = "1.0.1"
    # ipc.updateSnSecret(sn, model, version)
