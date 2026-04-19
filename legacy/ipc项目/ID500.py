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

    def __init__(self, base, app_user_id, token):
        self.base = base
        self.headers = {
            "authorization": token,
            "x-ugreen-app-system": app_system,
            "content-type": "application/json",
            "app_user_id": app_user_id,
            "countryCode": "CN",
            "language": "zh-Hans",

        }

    #   sn 检测
    def checkSN(self):
        data = {
            "productSerialNo": productModel,
            "sn": sn,
            "deviceType": deviceType,
        }
        data = json.dumps(data)
        path = "/app/v1/ipc/checkSn"
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

        path = "/app/v1/ipc/getMeta"
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

        path = "/app/v1/ipc/checkSign"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"校验签名", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   更新设备密钥
    def updateSnSecret(self, data):
        path = "/app/v1/ipc/updateSnSecret"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"更新设备密钥", reuslt.text)
        return json.loads(reuslt.text)["data"]


    #   解绑接口
    def unbind(self):
        data = {
            "deviceType": deviceType,
            "deviceUniqueCode": sn,
            "extra": {},
            "productSerialNo": productModel
        }

        data = json.dumps(data)

        path = "/rpc/v1/ipc/device/unBind"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"解绑接口", reuslt.text)

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

        path = "/rpc/v1/ipc/device/bind"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"绑定接口", reuslt.text)
        return json.loads(reuslt.text)

    # 获取bandToken接口
    def getBindToken(self):
        path = "/app/v1/ipc/getBindToken"
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

        path = "/app/v1/ipc/bindByToken"
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

    #   获取绑定信息
    def getBindInfo(self):
        data = {
            "sn": sn,
            "productSerialNo": productModel
        }
        data = json.dumps(data)

        path = "/app/v1/ipc/getBindInfo"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"获取绑定信息", reuslt.text)
        return json.loads(reuslt.text)["data"]

    #   根据bindToken查询绑定结果
    def getBindTokenResult(self, token):
        token = urllib.parse.quote(token)
        path = "/app/v1/ipc/getBindTokenResult?bindToken=" + token
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

        path = "/app/v1/ipc/updateSnSecret"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print(f"设备直接更新密钥", reuslt.text)
        saveSecret(sn, key)
        return json.loads(reuslt.text)["data"]
    # 根据语言获取所有标签
    def getAllLabels(self):
        path = "/app/v1/ipc/contact/getAllLabels"
        url = self.base + path
        result = requests.get(url, headers=self.headers)
        print("根据语言获取所有标签:" + result.text)
        return json.loads(result.text)

    # 获取标签用户
    def getUserLabel(self):
        path = f"/app/v1/ipc/contact/getUserLabels?productSerialNo={productModel}&deviceUniqueCode={sn}"
        url = self.base + path
        result = requests.get(url, headers=self.headers)
        print("获取标签用户:" + result.text)
        return json.loads(result.text)

    # 设置标签
    def setLabel(self):
        data = {
            "productSerialNo": productModel,
            "deviceUniqueCode": sn,
            "code": code,
            "userId": userId,
        }
        data = json.dumps(data)
        path = "/app/v1/ipc/contact/setLabel"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("设置标签:" + result.text)
        return json.loads(result.text)

    # 删除标签
    def delLabel(self):
        data = {
            "productSerialNo": productModel,
            "deviceUniqueCode": sn,
            "code": code,
            "userId": userId,
        }
        data = json.dumps(data)
        path = "/app/v1/ipc/contact/delLabel"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("删除标签:" + result.text)
        return json.loads(result.text)

    # 设备获取openId
    def getOpenIdByLabel(self):
        private_key, public_key, version = getKey(sn)
        data = {
            "productModel": productModel,
            "sn": sn,
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "version": version,
        }
        sort_data = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sort_data, private_key)
        data["sign"] = sign
        data["label"] = label
        data = json.dumps(data)
        path = "/app/v1/ipc/contact/getOpenIdByLabel"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("设备获取openId:" + result.text)
        return json.loads(result.text)
    # 获取全部标签
    def getDeviceAllOpenId(self):
        private_key, public_key, version = getKey(sn)
        data = {
            "productModel": productModel,
            "sn": sn,
            "mac": mac,
            "nonce": int(time.time() * 1000),
            "version": version,
        }
        sort_data = EccUtil.ascii_sort(data)
        sign = EccUtil.sign(sort_data, private_key)
        data["sign"] = sign
        data = json.dumps(data)
        path = "/app/v1/ipc/contact/getDeviceAllOpenId"
        url = self.base + path
        result = requests.post(url, headers=self.headers, data=data)
        print("获取全部标签:" + result.text)
        return json.loads(result.text)

    # 生成二维码
    def qrCode(self):
        data = {
            "productSerialNo": productModel,
            "deviceUniqueCode": sn,
            "role": role,
            "permission": permission,
        }
        data = json.dumps(data)
        path = "/app/v1/ipc/share/qrCode"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("生成二维码:" + reuslt.text)

    # 获取二维码信息
    def qrCodeInfo(self):
        data = {
            "qrCode": qrCode,
            "productSerialNo": productModel,
            "deviceUniqueCode": sn,
        }
        data = json.dumps(data)
        path = "/app/v1/ipc/share/qrCodeInfo"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("获取二维码信息:" + reuslt.text)

    # 接收二维码分享
    def qrCodeReceive(self):
        data = {
            "qrCode": qrCode,
            "productSerialNo": productModel,
            "deviceUniqueCode": sn,
        }
        data = json.dumps(data)
        path = "/app/v1/ipc/share/qrCodeReceive"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("接收二维码分享:" + reuslt.text)

    # 创建账号分享
    def account(self, receiver):
        data = {
            "productSerialNo": productModel,
            "deviceUniqueCode": sn,
            "role": role,
            "permission": permission,
            "receiver": receiver,
        }
        data = json.dumps(data)
        path = "/app/v1/ipc/share/account"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("创建账号分享:" + reuslt.text)

    # 获取账号分享列表
    def homeList(self):
        path = "/app/v1/ipc/share/homeList"
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
        path = "/app/v1/ipc/share/receive"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=data)
        print("接收，拒绝，接口:" + reuslt.text)

    # 设备分享列表
    def shareList(self):
        path = f"/app/v1/ipc/share/shareList?deviceUniqueCode={sn}&productSerialNo={productModel}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("设备分享列表:" + reuslt.text)

    # 取消分享
    def cancel(self, id):
        path = f"/app/v1/ipc/share/cancel/{id}"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers)
        print("取消分享:" + reuslt.text)

    # 设备信息
    def deviceInfo(self):
        path = f"/app/v1/ipc/share/deviceInfo?deviceUniqueCode={sn}&productSerialNo={productModel}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("设备信息:" + reuslt.text)
    # 根据ID查询分享信息
    def deviceInfoById(self):
        path = f"app/v1/ipc/share/deviceInfoById?id={id}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print("根据ID查询分享信息:" + reuslt.text)

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
    # 1310008 1268000
    userId = "1310008"
    app_user_id = "1268000"
    app_system = "ios"
    role = 1
    permission = "live,control"
    qrCode = ""
    # token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxNTAyNjMwMCIsIlVTRVJfQ09VTlRSWV9DT0RFIjoiQ04iLCJqdGkiOiIxNTAyNjMwMCIsImlhdCI6MTc2MTkwMjY0MSwiZXhwIjoxNzYxOTAzODQxfQ.lhhSaQBPcUu_EuReOkMtcz4BgELBm6ZnBsITQhc3_6s"
    # token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxNTAzMDUwMCIsIlVTRVJfQ09VTlRSWV9DT0RFIjoiQ04iLCJqdGkiOiIxNTAzMDUwMCIsImlhdCI6MTc2MTkwMzk3NywiZXhwIjoxNzYxOTA1MTc3fQ._YbDqvCMDGwF6_j0ACmaQOkMWNB1Tuyl1r_t7QZ5Jsw"
    # base = "https://test2.ugreeniot.com"
    base = "http://localhost:9017"
    ipc = ipc(base, app_user_id, token)
    if not getKey(sn):
        print(f"sn:{sn} 公私钥不存在")
        version = "1.0.0"
        ipc.snSubmitTest(version)
    privateKey, publicKey, version = getKey(sn)
    print(f"sn:{sn}：私钥privateKey:{privateKey}")
    print(f"sn:{sn}：公钥publicKey:{publicKey}")
    print(f"sn:{sn}：版本version:{version}")

############################设备绑定相关#########################################################
    # 校验SN
    # ipc.checkSN()
    # 获取三元组
    # ipc.getMeta(privateKey, version)

    # 校验签名
    # ipc.checkSign(privateKey, version)

    # 解绑设备
    # ipc.unbind()

    # app绑定设备
    # ipc.bind(privateKey, version)

    # 获取绑定token   查询绑定结果  根据bindToken 去绑定  查询 绑定结果
    # bindToken = ipc.getBindToken()["bindToken"]
    # ipc.getBindTokenResult(bindToken)
    # ipc.bindByToken(privateKey, version, bindToken)
    # ipc.getBindTokenResult(bindToken)

    # 获取绑定信息
    # ipc.getBindInfo()

    # 更新设备密钥
    version_new = "1.0.1"
    # ipc.updateSnSecretDevice(privateKey, version,version_new)

############################通话联系人###################################################

    # 获取标签
    # ipc.getAllLabels()
    #  获取用户标签
    # ipc.getUserLabel()
    #  设置标签
    code = "friend"
    # ipc.setLabel()
    #  删除标签
    # ipc.delLabel()
    # 根据标签获取用户openId
    label = "朋友"
    # ipc.getOpenIdByLabel()
    # 获取设备全部 用户的标签
    # ipc.getDeviceAllOpenId()

#############################设备分享##########################################
#########################################  二维码分享 ##########################################
    # 创建二维码
    # ipc.qrCode()
    # 扫码
    qrCode = "15714481124352"
    # ipc.qrCodeInfo()

    # 接收分享
    # ipc.qrCodeReceive()

    # 设备分享列表
    # ipc.shareList()

    # 分享者主动取消分享
    id = "119"
    # ipc.cancel(id)
    # 分享设备详情
    # ipc.deviceInfo()
    # ipc.deviceInfoById()
    #########################################  账号分享  ##########################################

    # 创建账号分享
    receiver = "1310008"
    # ipc.account(receiver)
    # 首页列表
    # ipc.homeList()
    # 接受
    id = "121"
    shareStatus = 1
    # ipc.receive()

    # 消息查询分享详情
    # ipc.deviceInfoById()


##############   设备网关测试      #######################
    headers = {
        "x-ugreen-sn": sn,
        "x-ugreen-mac": mac,
        "x-ugreen-nonce": str(int(time.time())),
        "x-ugreen-version": version,
        "x-ugreen-model": productModel,
        "x-ugreen-timestamp": str(int(time.time())),
    }
    data = EccUtil.ascii_sort(headers)
    sign = EccUtil.sign(data, privateKey)
    headers["x-ugreen-signature"] = sign
    # result = requests.get("http://localhost:9020/app/v1/software/ts", headers=headers)
    # print(result.text)
    xx = "BC:AD:AE:D7:BA:3D"
    # result = requests.get(f"http://localhost:9014/metadata/v1/factory/getSn?mac={xx}")
    result = requests.get(f"https://dev3.ugreeniot.com/metadata/v1/factory/getSn?mac={xx}")
    print(result.text)
