import request


class ipc_ota:
    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "language": "zh-Hans",
        }

    # 检测升级
    def check(self, serialNo):
        # 检测升级
        data = {
            "serialNo": serialNo,
            "versionCode": 0,
            "versionName": "sfsdfdsfsdfaetg qerg ",
        }
        path = "/app/v1/software/version/check_upgrade"
        self.client.request(method="post", path=path, data=data, headers=self.headers)


if __name__ == '__main__':

    ota = ipc_ota("ces")
    serialNo = "010001"
    ota.check(serialNo)

