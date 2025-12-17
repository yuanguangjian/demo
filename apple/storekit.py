import json
import requests
from appleToken import AppleToken
import appleVerify


# 查询订单详情
def getTransaction(transactionId, sandBox):
    url = ""
    product_url = f"https://api.storekit.itunes.apple.com/inApps/v1/transactions/{transactionId}"
    sandBox_url = f"https://api.storekit-sandbox.itunes.apple.com/inApps/v1/transactions/{transactionId}"
    if sandBox:
        url = sandBox_url
    else:
        url = product_url
    headers = {
        "Authorization": "Bearer " + AppleToken().get_storekit_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    signedTransactionInfo = result.json()["signedTransactionInfo"]
    if signedTransactionInfo:
        response = appleVerify.parse_signed_payload(signedTransactionInfo)
        print(json.dumps(response, indent=4, ensure_ascii=False))
        return response
    return None


# 查询历史订单
def getHistoryTransaction(transactionId, sandBox):
    url = ""
    product_url = f"https://api.storekit.itunes.apple.com/inApps/v2/history/{transactionId}"
    sandBox_url = f"https://api.storekit-sandbox.itunes.apple.com/inApps/v2/history/{transactionId}"
    if sandBox:
        url = sandBox_url
    else:
        url = product_url
    headers = {
        "Authorization": "Bearer " + AppleToken().get_storekit_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    signedTransactions = result.json()["signedTransactions"]
    transactionInfos = []
    if signedTransactions:
        for signedTransactionInfo in signedTransactions:
            response = appleVerify.parse_signed_payload(signedTransactionInfo)
            transactionInfos.append(response)
    transactionInfos = sorted(transactionInfos, key=lambda x: x["purchaseDate"])
    print(json.dumps(transactionInfos, indent=4, ensure_ascii=False))
    return transactionInfos


# 查询订阅状态
def getSubscriptionStatus(transactionId, sandBox):
    print("查询订阅状态")
    url = ""
    product_url = f"https://api.storekit.itunes.apple.com/inApps/v1/subscriptions/{transactionId}"
    sandBox_url = f"https://api.storekit-sandbox.itunes.apple.com/inApps/v1/subscriptions/{transactionId}"
    if sandBox:
        url = sandBox_url
    else:
        url = product_url
    headers = {
        "Authorization": "Bearer " + AppleToken().get_storekit_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    print(json.dumps(result.json(), indent=4, ensure_ascii=False))
    datas = result.json()["data"]
    if datas:
        for data in datas:
            groupId = data["subscriptionGroupIdentifier"]
            lastTransactions = data["lastTransactions"]
            for transaction in lastTransactions:
                originalTransactionId = transaction["originalTransactionId"]
                status = transaction["status"]
                signedTransactionInfo = transaction["signedTransactionInfo"]
                transactionInfos = appleVerify.parse_signed_payload(signedTransactionInfo)
                print("用户最新订单：", json.dumps(transactionInfos, indent=4, ensure_ascii=False))
                signedRenewalInfo = transaction["signedRenewalInfo"]
                renewalInfos = appleVerify.parse_signed_payload(signedRenewalInfo)
                print("用户最新订阅状态：", json.dumps(renewalInfos, indent=4, ensure_ascii=False))
    return None


# 查询退款订单
def getRefundHistory(transactionId, sandBox):
    print("查询退款历史")
    url = ""
    product_url = f"https://api.storekit.itunes.apple.com/inApps/v2/refund/lookup/{transactionId}"
    sandBox_url = f"https://api.storekit-sandbox.itunes.apple.com/inApps/v2/refund/lookup/{transactionId}"
    if sandBox:
        url = sandBox_url
    else:
        url = product_url
    headers = {
        "Authorization": "Bearer " + AppleToken().get_storekit_token(),
        "Content-Type": "application/json"
    }
    result = requests.get(url, headers=headers)
    print(json.dumps(result.json(), indent=4, ensure_ascii=False))
    signedTransactions = result.json()["signedTransactions"]
    if signedTransactions:
        for signedTransactionInfo in signedTransactions:
            response = appleVerify.parse_signed_payload(signedTransactionInfo)
            print(json.dumps(response, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    getTransaction("2000001072485485", True)
    # getHistoryTransaction("2000000957610744", True)
    # getSubscriptionStatus("2000001072120255", True)
    # getRefundHistory("2000000957610744", True)


    pass
