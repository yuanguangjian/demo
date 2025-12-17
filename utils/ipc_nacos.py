import requests
import EccUtil
import json


def login():
    url = "http://47.113.118.66:8848/nacos/v1/auth/users/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": "nacos",
        "password": "wz944308K2i41"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()["accessToken"]


def getService():
    path = "http://47.113.118.66:8848/nacos/v1/ns/catalog/instances?"
    data = {
        "accessToken": login(),
        "serviceName": "ugreen-dpt-metadata-consumer",
        "pageSize": 10,
        "pageNo": 1,
        "clusterName": "DEFAULT",
        "groupName": "DPT_GROUP_dev"
    }
    sorted = EccUtil.ascii_sort(data)
    url = path + sorted
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("请求失败")
        return
    if response.json()["count"] > 0:
        return response.json()["list"]


def setWeight():
    url = "http://47.113.118.66:8848/nacos/v1/ns/instance?"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    accessToken = login()
    url = url + "&accessToken=" + accessToken
    datas = getService()
    if datas :
        for data in datas:
            info = {}
            info["weight"] = 10
            info["groupName"] = "DPT_GROUP_dev"
            info["ip"] = data["ip"]
            info["port"] = data["port"]
            info["serviceName"] = "ugreen-dpt-metadata-consumer"
            info["clusterName"] = data["clusterName"]
            info["ephemeral"] = data["ephemeral"]
            info["enabled"] = data["enabled"]
            info["metadata"] = json.dumps(data["metadata"], separators=(',', ':'))
            response = requests.put(url, headers=headers, data=info)
            print(response.text)


if __name__ == '__main__':
    print("hello")
    # setWeight()
