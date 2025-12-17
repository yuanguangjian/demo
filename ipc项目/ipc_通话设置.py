import json
import requests
import time
import EccUtil

base = ""
token = ""
app_user_id = ""
productSerialNo = ""
deviceUniqueCode = ""
code = ""
userId = ""
mac = ""
label = ""


class ipc:

    def __init__(self):
        self.base = base
        self.headers = {
            "content-type": "application/json",
            "authorization": token,
            "app_user_id": app_user_id,
            "x-ugreen-app-system": "ios",
            "language": "zh-Hans",
        }

    # 根据语言获取所有标签
    def getAllLabels(self):
        path = "/app/v1/variety/contact/getAllLabels"
        url = self.base + path
        result = requests.get(url, headers=self.headers)
        print("根据语言获取所有标签:" + result.text)
        return json.loads(result.text)

    # 获取标签用户
    def getUserLabel(self):
        path = f"/app/v1/variety/contact/getUserLabels?productSerialNo={productSerialNo}&deviceUniqueCode={deviceUniqueCode}"
        url = self.base + path
        result = requests.get(url, headers=self.headers)
        print("获取标签用户:" + result.text)
        return json.loads(result.text)

    # 设置标签
    def setLabel(self):
        data = {
            "productSerialNo": productSerialNo,
            "deviceUniqueCode": deviceUniqueCode,
            "code": code,
            "userId": userId,
        }
        data = json.dumps(data)
        path = "/app/v1/variety/contact/setLabel"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("设置标签:" + result.text)
        return json.loads(result.text)

    # 删除标签
    def delLabel(self):
        data = {
            "productSerialNo": productSerialNo,
            "deviceUniqueCode": deviceUniqueCode,
            "code": code,
            "userId": userId,
        }
        data = json.dumps(data)
        path = "/app/v1/variety/contact/delLabel"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("删除标签:" + result.text)
        return json.loads(result.text)

    # 设备获取openId
    def getOpenIdByLabel(self):
        private_key, public_key, version = getKey(deviceUniqueCode)
        data = {
            "productModel": productSerialNo,
            "sn": deviceUniqueCode,
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "version": version,
        }
        sort_data = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sort_data, private_key)
        data["sign"] = sign
        data["label"] = label
        data = json.dumps(data)
        path = "/app/v1/variety/contact/getOpenIdByLabel"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("设备获取openId:" + result.text)
        return json.loads(result.text)
    # 获取全部标签
    def getDeviceAllOpenId(self):
        private_key, public_key, version = getKey(deviceUniqueCode)
        data = {
            "productModel": productSerialNo,
            "sn": deviceUniqueCode,
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "version": version,
        }
        sort_data = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sort_data, private_key)
        data["sign"] = sign
        data = json.dumps(data)
        path = "/app/v1/variety/contact/getDeviceAllOpenId"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("获取全部标签:" + result.text)
        return json.loads(result.text)

def getKey(sn):
    with open('key.json', 'r') as file:
        data = json.load(file)
    if sn in data:
        return data[sn]["privateKey"], data[sn]["publicKey"], data[sn]["version"]
    return None


if __name__ == '__main__':
    # base = "http://localhost:9010"
    base = "https://dev3.ugreeniot.com"
    token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjExODA1NDAsImV4cCI6MTc2MTMwMDU0MH0.3aLhyjOHIH3Vcg5ENsCodCjWEEdKfgiKJSRnp3Sy88s"
    productSerialNo = "Camera001"
    deviceUniqueCode = "I50000U58Q300098"
    app_user_id = "1268000"
    userId = "1268000"
    label = "朋友"
    code = "friend"
    mac = "mac"

    ipc = ipc()

    # 获取标签
    # ipc.getAllLabels()
    #  获取用户标签
    # ipc.getUserLabel()
    #  设置标签
    # ipc.setLabel()
    #  删除标签
    # ipc.delLabel()
    # 根据标签获取用户openId
    ipc.getOpenIdByLabel()
    # 获取设备全部 用户的标签
    ipc.getDeviceAllOpenId()

