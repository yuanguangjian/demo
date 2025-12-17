import requests
import json
import fileUtil
from ipc项目.login import UserInfo
import time


class Client():
    def __init__(self, env):
        self.env = env
        self.base = fileUtil.openFile("env.json")[env]
        print(f"请求的环境是：{self.base}")

    def request(self, method, headers, path, data):
        url = self.base + path
        print(f"请求地址：{url} 参数是：{data}")
        start = time.time()
        resp = requests.request(method=method, url=url, headers=headers, data=json.dumps(data))
        print(f"请求耗时：{time.time() - start} code：{resp.status_code}")
        if resp.status_code == 200:
            json_data = json.loads(resp.text)
            if json_data["code"] == 100003:
                user = UserInfo(self.base)
                account = fileUtil.openFile("login.json")[self.env]
                if self.env == "ces":
                    token = user.emailLogin(account)
                    headers["authorization"] = token
                else:
                    token = user.mobolePassowrdLoginxx(account)
                    headers["authorization"] = token
                return self.request(method, headers, path, data)
            else:
                print("结果是：\n" + json.dumps(json_data, indent=2, ensure_ascii=False))
                return json_data
        else:
            print(resp.text)


if __name__ == '__main__':
    pass
    # client = Client("dev")
    headers = {
        "content-type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJ1Z3JlZW4tc2lnbiIsImlzcyI6InVncmVlbi1zZXJ2aWNlIiwiZXhwIjoxNzY1NDU3NDk1fQ.KJKe4hiF8ZWD3A5LIoGg3Fs-8LtIaJEQbooDEQbmO1HHVETVyNNWyPQjNypBlJlnxr9jweb3Sj8APLdbQNKazQ"
    }
    # path = f"/app/v1/variety/ipc/eventRecord/list?sn=xxxx&productSerialNo=010001&size=1&page=10"
    # data = {}
    # result = client.request("get", headers, path, {})
    # print(result)

    data = {
        "sn": "O60001U59M200017",
        "productSerialNo": "010001",
        "size": 1,
        "page": 10
    }

    xx = requests.get(url="http://localhost:9024/api/v1/meta/test",headers=headers,data=json.dumps(data))
    print(xx.text)
