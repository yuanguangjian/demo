import requests

cfg = {
    "dvt": "https://cloudapi.iotrtc.cn/oam/ep/list?pageNo=1&pageSize=10&total=0",
    "ces": "https://os-console.iotrtc.cn/oam/ep/list?pageNo=1&pageSize=10&total=0&"
}

tk = "tk=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiMzI4IiwiMCIsIjcwZDY5ZGYyZTkwMDRkZThhNDUwYTA0YzkxYjhmZTRmIl0sImFjb2RlIjoiY2QwMDY5MmMzYmZlNTkyNjdkNWVjZmFjNTMxMDI4NmMiLCJleHAiOjE3NjM5OTI3NjJ9.ADawRKAL9qOzYHlwCrcj0t_NhFdonQSs0ZHZtIqqt_w"


class RTCXLogin:
    def __init__(self, env):
        self.env = env
        if env == "ces":
            self.url = cfg[env]
        else:
            self.url = cfg["dvt"]

    def getInfo(self, deviceName):
        base = None
        if deviceName:
            base = self.url + "&deviceName=" + deviceName
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "x-tk": tk,
        }
        response = requests.get(url=base, headers=headers)
        json = response.json()
        if json["code"] == 200:
            if json["data"]:
                if json["data"]["items"] and len(json["data"]["items"]) > 0:
                    data = json["data"]["items"][0]
                    deviceName = data["deviceName"]
                    onlineStatus = "离线"
                    if data["onlineStatus"] == 1:
                        onlineStatus = "在线"
                    print(f"相速平台：deviceName:{deviceName} onlineStatus:{onlineStatus} ")


if __name__ == '__main__':
    deviceName = "TYFEtGFgn0Jnkgwc9zjm"
    rtcx = RTCXLogin(env="ces")
    rtcx.getInfo(deviceName)
