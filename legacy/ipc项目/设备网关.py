import requests
import EccUtil

    headers = {
        "x-ugreen-sn": sn,
        "x-ugreen-mac": mac,
        "x-ugreen-nonce": str(int(time.time())),
        "x-ugreen-version": version,
        "x-ugreen-model": productModel,
        "x-ugreen-timestamp": str(int(time.time())),
    }
    data = EccUtil.ascii_sort(headers)
    sign = EccUtil.sign(data, privateKey)
    headers["x-ugreen-signature"] = sign
    result = requests.get("http://localhost:9020/app/v1/software/ts", headers=headers)
    print(result.text)