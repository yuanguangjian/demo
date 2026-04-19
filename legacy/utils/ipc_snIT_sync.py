import requests
import time
import hashlib
import json

config = {
    "dev": {
        "url": "https://test.ugreensmart.com/backend/d-wms/Api/OpenInbound/GetSNInboundRecordList",
        "appId": "UGTest001",
        "appKey": "dgugreenTest001",
    },
    "pro": {
        "url": "https://www.ugreensmart.com/backend/d-wms/Api/OpenInbound/GetSNInboundRecordList",
        "appId": "UG_pro_inner_001",
        "appKey": "dw#9DF4d2do&idwk24oaRTjdfEoijDeaw00I",
    }
}


class Sn():
    def __init__(self, env):
        self.env = env
        self.url = config[env]["url"]
        self.appId = config[env]["appId"]
        self.appKey = config[env]["appKey"]

    def get_md5(self, text):
        # 将字符串编码为字节
        byte_data = text.encode('utf-8')
        # 创建 MD5 对象
        md5 = hashlib.md5()
        # 更新数据
        md5.update(byte_data)
        # 返回十六进制结果
        return md5.hexdigest()

    def asyncData(self, data):
        sencodes = int(time.time())
        u_stamp = sencodes
        serct = f"{self.appId}{sencodes}{self.appKey}"
        u_secret = self.get_md5(serct)
        headers = {
            "Content-Type": "application/json",
            "u-appid": self.appId,
            "u-stamp": str(u_stamp),
            "u-secret": u_secret,
        }
        data = json.dumps(data)
        print("请求参数："+data)
        print("请求地址："+self.url)
        result = requests.post(url=self.url, headers=headers, data=data)
        print(f"请求结果是：{result.text}")


if __name__ == '__main__':
    product_no = "ID500 Pro"
    data = {
        # "ProductNos": ["CM316"],
        "ProductNos": ["ID500 Pro"],
        # "SKUs":["85374"],
        "LastDateStart": "2025-11-19 00:00:00",
        "LastDateEnd": "2025-11-26 00:00:00",
        "PageSize": "100",
        "Page": "1",
    }

    sn = Sn("pro")
    sn.asyncData(data)
