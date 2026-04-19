import requests
import time
import hashlib
import json

url = "https://test.ugreensmart.com/backend/d-wms/Api/OpenInbound/GetSNInboundRecordList"
u_appid = "UGTest001"
u_secret = "dgugreenTest001"

sencodes =int(time.time())

def get_md5(text):
    # 将字符串编码为字节
    byte_data = text.encode('utf-8')
    # 创建 MD5 对象
    md5 = hashlib.md5()
    # 更新数据
    md5.update(byte_data)
    # 返回十六进制结果
    return md5.hexdigest()


u_stamp = sencodes
serct = f"{u_appid}{sencodes}{u_secret}"
u_secret = get_md5(serct)

headers = {
    "Content-Type": "application/json",
    "u-appid": u_appid,
    "u-stamp": str(u_stamp),
    "u-secret": u_secret,
}

data = {
    "ProductNos":["CM316"],
    "LastDateStart":"2025-10-15 00:00:00",
    "LastDateEnd":"2025-10-18 00:00:00",
    "PageSize":"1",
    "Page":"1",
}

print(f"请求header是：{headers}")
print(f"请求参数是：{data}")
data = json.dumps(data)
result  = requests.post(url, headers=headers,data=data)
print(result.text)


