import json
import time
import sys
import requests
import EccUtil  # 请确保你有这个模块


class IpcClient:
    def __init__(self, base_url, user_id, token):
        self.base_url = base_url
        self.headers = {
            "authorization": token,
            "x-ugreen-app-system": "ios",
            "content-type": "application/json",
            "app_user_id": user_id
        }

    def _request(self, method, path, data=None):
        url = self.base_url + path
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            else:
                response = requests.post(url, headers=self.headers, data=data)
            print(f"[{method}] {path} → {response.status_code}")
            return json.loads(response.text).get("data")
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def get_app_info(self, platform):
        return self._request("GET", f"/app/v1/variety/getAppInfo?platform={platform}")

    def check_sn(self, data):
        return self._request("POST", "/app/v1/variety/checkSn", data)

    def get_meta(self, data):
        return self._request("POST", "/app/v1/variety/getMeta", data)

    def check_sign(self, data):
        return self._request("POST", "/app/v1/variety/checkSign", data)

    def update_sn_secret(self, data):
        return self._request("POST", "/app/v1/variety/updateSnSecret", data)

    def update_device_info(self, data):
        return self._request("POST", "/app/v1/variety/updateDeviceInfo", data)

    def device_list(self):
        return self._request("GET", "/app/v1/variety/deviceList")

    def unbind(self, data):
        return self._request("POST", "/app/v1/variety/unbind", data)

    def bind(self, data):
        return self._request("POST", "/app/v1/variety/bind", data)

    def get_bind_token(self):
        return self._request("GET", "/app/v1/variety/getBindToken")

    def bind_by_token(self, data):
        return self._request("POST", "/app/v1/variety/bindByToken", data)


def load_key(sn):
    try:
        with open('key.json', 'r') as f:
            data = json.load(f)
        return data.get(sn)
    except Exception as e:
        print(f"读取密钥失败: {e}")
        return None


def prepare_sign_data(sn, mac, model, version):
    return {
        "mac": mac,
        "nonce": int(time.time() * 1000),
        "productModel": model,
        "sn": sn,
        "version": version
    }


def sign_payload(payload, private_key):
    sorted_data = EccUtil.ascii_sort(payload)
    payload["sign"] = EccUtil.sign(sorted_data, private_key)
    return payload


if __name__ == '__main__':
    sn = "I50000U57Q200006"
    mac = sn
    model = "Camera001"
    device_type = "ipc_camera"
    user_id = "1268000"
    token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    base_url = "https://test2.ugreeniot.com"

    key_info = load_key(sn)
    if not key_info:
        print(f"sn:{sn} 公私钥不存在")
        sys.exit(1)

    private_key = key_info["privateKey"]
    public_key = key_info["publicKey"]
    version = key_info["version"]

    print(f"sn:{sn}\n私钥:{private_key}\n公钥:{public_key}\n版本:{version}")

    client = IpcClient(base_url, user_id, token)

    # 获取三元组
    payload = prepare_sign_data(sn, mac, model, version)
    payload = sign_payload(payload, private_key)
    payload["deviceType"] = device_type
    payload["productSerialNo"] = model
    client.get_meta(json.dumps(payload))

    # 获取绑定 Token 并绑定设备
    bind_token = client.get_bind_token().get("bindToken")
    payload = prepare_sign_data(sn, mac, model, version)
    payload = sign_payload(payload, private_key)
    payload["bindToken"] = bind_token
    client.bind_by_token(json.dumps(payload))

    # 更新设备密钥
    new_private, new_public = EccUtil.genKey()
    new_version = "1.0.0"
    update_payload = {
        "mac": mac,
        "nonce": int(time.time() * 1000),
        "productModel": model,
        "sn": sn,
        "version": new_version,
        "oldVersion": version,
        "publicKey": new_public
    }
    update_payload = sign_payload(update_payload, private_key)
    client.update_sn_secret(json.dumps(update_payload))
