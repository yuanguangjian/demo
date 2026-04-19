import request
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


class ipc_share():

    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios"
        }

    #   获取sid
    def getSidInfo(self):
        data = {}
        path = "/app/v1/user/security/getSidInfo"
        j = self.client.request("post", path=path, headers=self.headers, data=data)
        if j["code"] == 100000:
            return j["data"]["sid"], j["data"]["publicKey"]

    # 加密数据
    def encode_data(self, d, publicKey):
        MAX_ENCRYPT_BLOCK = 256
        # 将 Base64 编码的密钥解码
        key_bytes = base64.b64decode(publicKey)
        # 使用 RSA 密钥对进行解密/加密
        key = RSA.import_key(key_bytes)
        cipher = PKCS1_v1_5.new(key)
        json_str = d
        print(f"encodeData:{json_str}")
        data = json_str.encode('utf-8')
        input_len = len(data)
        encrypted_data = bytearray()
        off_set = 0
        # 分段加密
        while input_len - off_set > 0:
            # 如果数据长度大于最大加密块，则分段处理
            if input_len - off_set > MAX_ENCRYPT_BLOCK:
                encrypted_data.extend(cipher.encrypt(data[off_set: off_set + MAX_ENCRYPT_BLOCK]))
            else:
                encrypted_data.extend(cipher.encrypt(data[off_set:]))
            off_set += MAX_ENCRYPT_BLOCK
        return base64.b64encode(encrypted_data).decode('utf-8')

    # 校验账号
    def checkAccount(self, phone, sid):
        data = {
            "sid": sid,
            "account": phone
        }
        path = "/app/v1/user/checkAccount"
        self.client.request("post", path=path, headers=self.headers, data=data)

    # 生成二维码
    def qrCode(self, sn, model, role, permission):
        data = {
            "productSerialNo": model,
            "deviceUniqueCode": sn,
            "role": role,
            "permission": permission,
        }
        path = "/app/v1/variety/share/qrCode"
        self.client.request(method="post", headers=self.headers, data=data, path=path)

    # 获取二维码信息
    def qrCodeInfo(self, qrCode, sn, model):
        data = {
            "qrCode": qrCode,
            "productSerialNo": model,
            "deviceUniqueCode": sn,
        }
        path = "/app/v1/variety/share/qrCodeInfo"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    # 接收二维码分享
    def qrCodeReceive(self, qrCode, sn, model):
        data = {
            "qrCode": qrCode,
            "productSerialNo": model,
            "deviceUniqueCode": sn,
        }
        path = "app/v1/variety/share/qrCodeReceive"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    # 创建账号分享
    def account(self, sn, model, role, permission, receiver):
        data = {
            "productSerialNo": model,
            "deviceUniqueCode": sn,
            "role": role,
            "permission": permission,
            "receiver": receiver,
        }
        path = "app/v1/variety/share/account"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    # 获取账号被分享列表
    def homeList(self):
        data = {}
        path = "app/v1/variety/share/homeList"
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    # 接收，拒绝，接口
    def receive(self, id, shareStatus):
        data = {
            "id": id,
            "shareStatus": shareStatus,
        }
        path = "app/v1/variety/share/receive"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    # 设备分享列表
    def shareList(self, sn, model):
        data = {}
        path = f"app/v1/variety/share/shareList?deviceUniqueCode={sn}&productSerialNo={model}"
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    # 取消分享
    def cancel(self, id):
        path = f"app/v1/variety/share/cancel/{id}"
        self.client.request(method="post", path=path, headers=self.headers, data=data)

    # 设备信息
    def deviceInfo(self, sn, model):
        data = {}
        path = f"app/v1/variety/share/deviceInfo?deviceUniqueCode={sn}&productSerialNo={model}"
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    # 根据ID查询分享信息
    def deviceInfoById(self, id):
        data = {}
        path = f"app/v1/variety/share/deviceInfoById?id={id}"
        self.client.request(method="get", path=path, headers=self.headers, data=data)

    # 查询消息
    def msg_list(self):
        data = {}
        path = f"/app/v1/variety/message/pagination?page=1&size=100"
        self.client.request(method="get", path=path, headers=self.headers, data=data)


if __name__ == '__main__':
    ipc = ipc_share("dev")

    # sid, publicKey = ipc.getSidInfo()
    # 加密数据
    phone = "15338849809"
    # phone = ipc.encode_data(phone, publicKey)
    # 校验账号
    # ipc.checkAccount(phone, sid)
    # 获取用户信息
    # ipc.getUserInfo("1310008")

    sn = "I50000U58Q300098"
    model = "010001"
    role = "1"
    permission = "live,control"


    # ipc.qrCode(sn, model, role, permission)

    # ipc.qrCodeInfo(sn, model, model)

    qrCode = ""

    # ipc.qrCodeReceive(qrCode, sn, model)

    # ipc.account(sn, model, role, permission, receiver)
