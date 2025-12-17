import requests
import jwt_token
import json
import fileUtil
import EccUtil

privateKey = "MEECAQAwEwYHKoZIzj0CAQYIKoZIzj0DAQcEJzAlAgEBBCABytI6RcuA8rqPnkBOqtjmsTk0vL1oPE1jAT/8DO2/ew=="
sn = ""
model = ""


class Client:
    def __init__(self, env):
        self.env = fileUtil.openFile("env.json")[env]
        print(f"请求的环境是：{self.env}")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + jwt_token.generate_token(privateKey)
        }

    def checkSn(self):
        url = self.env + "/api/v1/meta/checkSn"
        data = {
            "sn": sn,
            "productModel": model
        }
        result = requests.post(url=url, headers=self.headers, data=json.dumps(data))
        print(json.dumps(result.json(), indent=4, ensure_ascii=False))
        return result.json()

    def getSnMetadata(self):
        url = self.env + "/api/v1/meta/getMeta"
        snInfo = fileUtil.getSnSecret(model, sn, "device")
        if not snInfo:
            print("没有找到密钥")
            return None
        data = {
            "sn": sn,
            "productModel": model,
            "version": snInfo["version"],
        }
        result = requests.post(url=url, headers=self.headers, data=json.dumps(data))
        print(json.dumps(result.json(), indent=4, ensure_ascii=False))
        return result.json()

    def getSnSecret(self):
        url = self.env + "/api/v1/meta/getSnSecretV2"
        snInfo = fileUtil.getSnSecret(model, sn, "device")
        if not snInfo:
            print("没有找到密钥")
            return None
        data = {
            "sn": sn,
            "productModel": model,
            "version": snInfo["version"],
        }
        result = requests.post(url=url, headers=self.headers, data=json.dumps(data))
        print(json.dumps(result.json(), indent=4, ensure_ascii=False))
        return result.json()

    def updateSnSecret(self):
        url = self.env + "/api/v1/meta/updateSnSecret"
        snInfo = fileUtil.getSnSecret(model, sn, "device")
        if not snInfo:
            print("没有找到密钥")
            return None
        privateKey, publicKey = EccUtil.genKey()
        newVersion = "1.0.5"
        data = {
            "sn": sn,
            "productModel": model,
            "version": newVersion,
            "oldVersion": snInfo["version"],
            "publicKey": publicKey
        }
        value = {
            "publicKey": publicKey,
            "version": newVersion,
            "privateKey": privateKey
        }
        result = requests.post(url=url, headers=self.headers, data=json.dumps(data))
        data = result.json()
        if data and data["code"] == 100000:
            key = f"{model}_{sn}"
            fileUtil.saveSnSecret(key, value, "device")
        print(json.dumps(result.json(), indent=4, ensure_ascii=False))
        return data


if __name__ == '__main__':
    sn = "I50000U57Q200017"
    model = "00000"

    client = Client("device")
    client.checkSn()
    client.getSnMetadata()
    client.getSnSecret()
    client.updateSnSecret()
