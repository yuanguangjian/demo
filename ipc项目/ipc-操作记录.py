import json
import requests

base = ""
token = ""
app_user_id = ""
sn = ""
productSerialNo = ""
page = 1
size = 10


class ipc:

    def __init__(self):
        self.base = base
        self.headers = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "x-ugreen-app-deviceType": "OPPO R9S"
        }

    # 新增操作记录
    def add(self):
        data = {
            "sn": sn,
            "productSerialNo": productSerialNo
        }
        path = base + "/app/v1/variety/ipc/eventRecord/add"
        data = json.dumps(data)
        result = requests.post(path, data=data, headers=self.headers)
        print("新增操作记录:", result.text)

    # 查询列表
    def list(self):
        path = base + f"/app/v1/variety/ipc/eventRecord/list?sn={sn}&productSerialNo={productSerialNo}&size={size}&page={page}"
        result = requests.get(path, headers=self.headers)
        print("查询列表:", result.text)


if __name__ == '__main__':
    base = "https://iot-test.ugreeniot.com"
    # base = "https://dev3.ugreeniot.com"
    # base = "http://localhost:9010"
    # base = "https://test2.ugreeniot.com"
    sn = "I50000U57Q2100OP"
    productSerialNo = "Camera001"
    app_user_id = "1268000"
    token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjY4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyNjgwMDAiLCJpYXQiOjE3NjMwODI3MzYsImV4cCI6MTc2MzIwMjczNn0.8xds39UwjSuaRTg7QQaLKpEl0ai0YoSjS0uWN3u7jaE"
    ipc = ipc()

    # ipc.add()

    ipc.list()
