import request

countryCode="CN"

class Product:
    def __init__(self, env):
        self.env = env
        self.client = request.Client(self.env)
        self.headers = {
            "content-type": "application/json",
            "x-ugreen-app-system": "ios",
            "language": "zh-Hans",
        }

    # 获取产品列表
    def getProductList(self):
        self.headers["countryCode"] = countryCode
        data = {}
        path = "/app/v1/product/model/list_issued_v2"
        self.client.request(method="get", path=path, data=data, headers=self.headers)

    def getProductList2(self):
        self.headers["countryCode"] = countryCode
        data = {}
        path = "/app/v1/product/xxxxx"
        self.client.request(method="get", path=path, data=data, headers=self.headers)

if __name__ == '__main__':

    # CN US
    countryCode = "us"
    product = Product("ces")
    for i in range(20):
        product.getProductList()
