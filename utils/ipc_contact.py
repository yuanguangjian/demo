import request
import fileUtil
import time
import EccUtil


class ipcContact():
    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "language": "zh-Hans",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMzAyMDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEzMDIwMDAiLCJpYXQiOjE3NjUzMzA2NjIsImV4cCI6MTc2NTQ1MDY2Mn0.5tC1LXWw7lhYXm2Duf5k9Nyv7gqrFbr4skQkryedizM"
        }

    # 根据语言获取所有标签
    def getAllLabels(self):
        data = {}
        path = "/app/v1/variety/contact/getAllLabels"
        self.client.request(method="get", path=path, data=data, headers=self.headers)

    # 获取标签用户
    def getUserLabel(self, sn, model):
        data = {}
        path = f"/app/v1/variety/contact/getUserLabels?productSerialNo={model}&deviceUniqueCode={sn}"
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    # 设置标签
    def setLabel(self, sn, model, code, userId):
        data = {
            "productSerialNo": model,
            "deviceUniqueCode": sn,
            "code": code,
            "userId": userId,
        }
        path = "/app/v1/variety/contact/setLabel"
        self.client.request(method="post", path=path, data=data, headers=self.headers)

    # 删除标签
    def delLabel(self, sn, model, code, userId):
        data = {
            "productSerialNo": model,
            "deviceUniqueCode": sn,
            "code": code,
            "userId": userId,
        }
        path = "/app/v1/variety/contact/delLabel"
        self.client.request(method="post", path=path, data=data, headers=self.headers)

    # 设备获取openId
    def getOpenIdByLabel(self, sn, model, label):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getOpenIdByLabel 密钥不存在哦")
            return
        private_key = snInfo["privateKey"]
        version = snInfo["version"]
        data = {
            "productModel": model,
            "sn": sn,
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "version": version,
        }
        sort_data = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sort_data, private_key)
        data["sign"] = sign
        data["label"] = label
        path = "/app/v1/variety/contact/getOpenIdByLabel"
        self.client.request(method="post", path=path, data=data, headers=self.headers)

    # 获取全部标签
    def getDeviceAllOpenId(self, sn, model):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        if not snInfo:
            print("getOpenIdByLabel 密钥不存在哦")
            return
        private_key = snInfo["privateKey"]
        version = snInfo["version"]
        data = {
            "productModel": model,
            "sn": sn,
            "mac": sn,
            "nonce": int(time.time() * 1000),
            "version": version,
        }
        sort_data = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sort_data, private_key)
        data["sign"] = sign
        path = "/app/v1/variety/contact/getDeviceAllOpenId"
        self.client.request(method="post", path=path, data=data, headers=self.headers)


if __name__ == '__main__':
    ipc = ipcContact("dvt")

    sn = "I50001A5JE200035"
    model = "010001"

    ipc.getAllLabels()
    # ipc.getUserLabel(sn, model)

    code = "daughter"
    userId = "1310003"
    # ipc.setLabel(sn, model, code, userId)
    # ipc.delLabel(sn, model, code, userId)

    label = "label"
    # ipc.getOpenIdByLabel(sn, model, label)
    #
    # ipc.getDeviceAllOpenId(sn, model)
