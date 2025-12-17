import request
import time
import fileUtil
import EccUtil


class Device:
    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-ugreen-app-system": "ios",
            "app_user_id":"1326011"
        }

    def device(self, sn, productModel, method, path, params):
        snInfo = fileUtil.getSnSecret(productModel, sn, self.env)
        if snInfo:
            privateKey = snInfo["privateKey"]
            version = snInfo["version"]
            header = {
                "x-ugreen-sn": sn,
                "x-ugreen-mac": sn,
                "x-ugreen-nonce": str(int(time.time())),
                "x-ugreen-version": version,
                "x-ugreen-model": productModel,
                "x-ugreen-algorithm": "01",
            }
            data = EccUtil.ascii_sort(header)
            sign = EccUtil.sign(data, privateKey)
            header["x-ugreen-signature"] = sign
            headers = self.headers.copy()
            headers["x-ugreen-sn"] = header["x-ugreen-sn"]
            headers["x-ugreen-mac"] = header["x-ugreen-mac"]
            headers["x-ugreen-nonce"] = header["x-ugreen-nonce"]
            headers["x-ugreen-version"] = header["x-ugreen-version"]
            headers["x-ugreen-model"] = header["x-ugreen-model"]
            headers["x-ugreen-algorithm"] = header["x-ugreen-algorithm"]
            headers["x-ugreen-signature"] = header["x-ugreen-signature"]
            return self.client.request(method=method, path=path, headers=headers, data=params)
        else:
            print("经过设备网关的接口，没有找到密钥")
            return None

    # 绑定接口
    def bindByToken(self, sn, model, token):
        path = "/device/v1/variety/bindByToken"
        snInfo = fileUtil.getSnSecret(model, sn, self.env)
        params = {
            "bindToken": token,
            "sn": sn,
            "productModel": model,
            "version": snInfo["version"],
            "mac":sn,
            "algorithm":"01"
        }
        self.device(sn, model, "post", path, params)

    # 根据标签获取openId
    def getOpenIdByLabel(self, sn, model, label):
        path = "/device/v1/variety/contact/getOpenIdByLabel"
        params = {
            "label": label,
            "sn": sn,
            "productModel": model
        }

        # 获取设备的全部标签
        self.device(sn, model, "post", path, params)

    def getDeviceAllOpenId(self, sn, model):
        path = "/device/v1/variety/contact/getDeviceAllOpenId"
        params = {
            "sn": sn,
            "productModel": model
        }
        self.device(sn, model, "post", path, params)

    def updateSnSecret(self, sn, model, version):
        snInfo = fileUtil.getSnSecret(model, sn, self.env)

        privateKey, publicKey = EccUtil.genKey()
        path = "/device/v1/variety/updateSnSecret"
        params = {
            "newVersion": version,
            "newAlgorithm": "01",
            "publicKey": publicKey,
            "sn": sn,
            "productModel": model,
            "version": snInfo["version"],
            "algorithm": "01"
        }
        result =self.device(sn, model, "post", path, params)
        value = {
            "privateKey": privateKey,
            "version": version,
            "publicKey": publicKey,
        }
        if result and result["code"] == 100000:
            key = f"{model}_{sn}"
            fileUtil.saveSnSecret(key, value, self.env)



if __name__ == '__main__':

    device = Device("device")
    # sn = "I50000U57Q200017"
    sn = "I50000U57Q200017"
    model = "00000"
    token = "GP7hJQiTsUtfp/JvNd/SXQ=="

    device.bindByToken(sn, model, token)
    # device.getDeviceAllOpenId(sn,model)
    # device.getOpenIdByLabel(sn, model, "xxx")
    # device.updateSnSecret(sn, model, "1.0.6")