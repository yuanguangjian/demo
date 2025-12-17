import request


class IPCEventRecord():

    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "x-ugreen-app-deviceType": "OPPO R9S",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJXZWIiLCJzdWIiOiJVR1JFRU4tRFBUIiwiaXNzIjoiVUdSRUVOLURQVCIsIkxPR0lOX1VTRVJfSUQiOiIxMjg4MDAwIiwiVVNFUl9DT1VOVFJZX0NPREUiOiJDTiIsImp0aSI6IjEyODgwMDAiLCJpYXQiOjE3NjUxNzUzMDgsImV4cCI6MTc2NTI5NTMwOH0.HGyaYzJt7tSjXWOoaHrnGtZzMx4IoZyL6n1ar8wZ4oE"
        }

    def addEvent(self, sn, model):
        data = {
            "sn": sn,
            "productSerialNo": model
        }
        path = "/app/v1/variety/ipc/eventRecord/add"
        self.client.request(method="post", path=path, data=data, headers=self.headers)

    def listEvent(self, sn, model, page, size):
        data = {}
        path = f"/app/v1/variety/ipc/eventRecord/list?sn={sn}&productSerialNo={model}&size={size}&page={page}"
        self.client.request(method="get", path=path, headers=self.headers, data=data)


if __name__ == '__main__':
    sn = "I50001B5J6200024"
    model = "010001"
    page = 2
    size = 20
    ipc = IPCEventRecord("dvt")

    # ipc.addEvent(sn, model)
    ipc.listEvent(sn, model, page, size)
