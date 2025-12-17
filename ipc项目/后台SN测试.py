import json

import requests
import EccUtil
import time, sys

from ipc项目.ipc_通话设置 import productSerialNo

token = ""
base = ""

productName = ""
productNo = ""
productSerialNo = ""
id = ""
sn = ""
firstStartTime = ""
firstEndTime = ""
secondStartTime = ""
secondEndTime = ""
status = ""
page = 1
size = 10

class ipc:

    def __init__(self, base, token):
        self.base = base
        self.headers = {
            "authorization": token,
            "content-type": "application/json",
        }

    # 新增
    def add(self):
        data = {
            "productName": productName,
            "productNo": productNo,
            "productSerialNo": productSerialNo,
        }

        path = "/admin/v1/variety/sn/productIt/add"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=json.dumps(data))
        print(f"新增", reuslt.text)
        return json.loads(reuslt.text)["data"]

    # 编辑
    def edit(self):

        data = {
            "id": id,
            "productName": productName,
            "productSerialNo": productSerialNo,
            "productNo": productNo,
        }

        path = "/admin/v1/variety/sn/productIt/edit"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers, data=json.dumps(data))
        print(f"编辑", reuslt.text)
        return json.loads(reuslt.text)["data"]

    # 删除
    def delete(self):
        path = f"/admin/v1/variety/sn/productIt/del/{id}"
        url = self.base + path
        reuslt = requests.post(url, headers=self.headers)
        print(f"删除", reuslt.text)
        return json.loads(reuslt.text)["data"]

    # 列表
    def list(self):
        data = {
            "productName": "",
            "productNo": "",
            "productSerialNo": "",
            "page": page,
            "size": size
        }
        data = EccUtil.ascii_sort(data)

        path = f"/admin/v1/variety/sn/productIt/list?{data}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(f"获取列表", reuslt.text)
        return json.loads(reuslt.text)["data"]

    # sn列表
    def sn(self):
        data = {
            "productName": productName,
            "sn": sn,
            "firstStartTime": firstStartTime,
            "firstEndTime": firstEndTime,
            "scanStartTime": secondStartTime,
            "scanEndTime": secondEndTime,
            "status": status,
            "page": page,
            "size": size
        }
        data = EccUtil.ascii_sort(data)

        path = f"/admin/v1/variety/sn/list?{data}"
        url = self.base + path
        reuslt = requests.get(url, headers=self.headers)
        print(f"sn列表", reuslt.text)
        return json.loads(reuslt.text)["data"]

if __name__ == '__main__':
    token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxIiwiVVNFUl9DT1VOVFJZX0NPREUiOiIiLCJqdGkiOiIxIiwiaWF0IjoxNzU5OTk4NDk3LCJleHAiOjE3NjAwMDU2OTd9.4BjML2DpveQjTf8MXcniKWI6VZGkrISEE-PAwnSjJUg"
    # base = "https://dev3.ugreeniot.com"
    base = "http://localhost:9010"

    ipc = ipc(base, token)


    # firstStartTime = int(time.time() * 1000)
    # firstEndTime = int(time.time() * 1000)
    page = 1
    size = 10

    # productName = "hello"
    # productNo = "8888xxx90"
    # productSerialNo = "Camera003"
    # status = "2"
    # sn = "I50000U58Q200012"
    id = "8"

    # 新增
    # ipc.add()
    # 编辑
    # ipc.edit()
    # 删除
    # ipc.delete()
    # it 部 录入列表
    # ipc.list()
    # sn 列表
    ipc.sn()
