import json

import requests
from appleToken import AppleToken


# 获取非订阅产品列表
def getInAppPurchaseProducts():
    print("获取非订阅产品列表")
    token = AppleToken()
    url = "https://api.appstoreconnect.apple.com/v1/apps/6499123394/inAppPurchasesV2"
    headers = {
        "Authorization": "Bearer " + token.get_connect_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    data = result.json()["data"]
    products = []
    for item in data:
        product = {
            "type": item["type"],
            "id": item["id"],
            "name": item["attributes"]["name"],
            "productId": item["attributes"]["productId"],
            "inAppPurchaseType": item["attributes"]["inAppPurchaseType"],
            "state": item["attributes"]["state"]
        }
        products.append(product)
    print(json.dumps(products, indent=4, ensure_ascii=False))
    return products


# 获取组
def getGroups():
    print("获取订阅组")
    token = AppleToken()
    url = "https://api.appstoreconnect.apple.com/v1/apps/6499123394/subscriptionGroups"
    headers = {
        "Authorization": "Bearer " + token.get_connect_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    data = result.json()["data"]
    groups = []
    for item in data:
        group = {
            "name": item["attributes"]["referenceName"],
            "id": item["id"]
        }
        groups.append(group)
    return groups


def getProductByGroupId():
    print("获取组内订阅产品")
    token = AppleToken()
    headers = {
        "Authorization": "Bearer " + token.get_connect_token(),
        "Content-Type": "application/json"
    }
    groups = getGroups()
    products = []
    for group in groups:
        groupId = group["id"]
        url = f"https://api.appstoreconnect.apple.com/v1/subscriptionGroups/{groupId}/subscriptions"
        result = requests.get(url, headers=headers)
        product = {}
        product["groupName"] = group["name"]
        product["groupId"] = group["id"]
        items = []
        for item in result.json()["data"]:
            row = {
                "id": item["id"],
                "name": item["attributes"]["name"],
                "productId": item["attributes"]["productId"],
                "subscriptionPeriod": item["attributes"]["subscriptionPeriod"],
                "state": item["attributes"]["state"],
                "groupLevel": item["attributes"]["groupLevel"],
            }
            items.append(row)
        sorted_items = sorted(items, key=lambda x: x["groupLevel"])
        product["items"] = sorted_items
        products.append(product)
    print(json.dumps(products, indent=4, ensure_ascii=False))
    return products

# 获取产品详情 一次性内购的产品详情 6749221430
def getProductDetailInAppPurchases(productId):
    print("获取产品详情")
    url = f"https://api.appstoreconnect.apple.com/v2/inAppPurchases/{productId}"
    token = AppleToken()
    headers = {
        "Authorization": "Bearer " + token.get_connect_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    print(json.dumps(result.json(), indent=4, ensure_ascii=False))


# 获取产品详情  订阅的产品详情  6748303946
def getProductDetailSubscriptions(productId):
    print("获取产品详情")
    url = f"https://api.appstoreconnect.apple.com/v1/subscriptions/{productId}"
    token = AppleToken()
    headers = {
        "Authorization": "Bearer " + token.get_connect_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    print(json.dumps(result.json(), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    # getGroups()
    # getInAppPurchaseProducts()
    getProductByGroupId()
    # getProductDetailInAppPurchases("6748303946")
    # getProductDetailInAppPurchases("6749221430")