import re
import requests
import json

def extract_curl_info(curl_command):
    # 提取 URL
    url_match = re.search(r"curl\s+'([^']+)'", curl_command)
    url = url_match.group(1) if url_match else None
    # 提取头部信息
    headers = {}
    header_matches = re.findall(r"-H\s+'([^:]+): ([^']+)'", curl_command)
    for match in header_matches:
        headers[match[0]] = match[1]
    # 提取请求体
    data_match = re.search(r"--data-raw\s+'([^']+)'", curl_command)
    data = data_match.group(1) if data_match else None
    return url, headers, data


def getContent():
    getContent = """curl 'https://dev.vivo.com.cn/webapi/comment/info/list?timestamp=1751608727527' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: b_account_username=v7Wf3wBcfM9BfB8CB0Q6KQ%3D%3D; b_account_aid=s9oXesI7rcg%3D; b_account_token=33172ca3e57108a1c1525bf5e326e7ca.1751090349380; b_account_salt=Hz71UDRV%2BFX4fbJzhXKirg%3D%3D.1751608749380; JSESSIONID=09B762E8789732241A9C0E47A3D55BDE' \
  -H 'Origin: https://dev.vivo.com.cn' \
  -H 'Referer: https://dev.vivo.com.cn/comment/tab/appStoreDetails?id=603017&packageName=com.ugreen.iot&appType=1' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'csrfToken: nBBGv7' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'v-source: 2c3057c01591e7aa94805e6435cddd50' \
  --data-raw '{"model":"","starRating":"","appVersion":"","endDate":"2025-07-04 23:59:59","startDate":"2025-06-03 00:00:00","currentPageNum":1,"pageSize":10,"packageName":"com.ugreen.iot","sort":2,"replyStatus":""}' \
  --compressed"""
    url, headers, data = extract_curl_info(getContent)
    content = requests.post(url, headers=headers, data=data)
    return json.loads(content.text)


def getCore():
    getCore = """curl 'https://dev.vivo.com.cn/webapi/comment/info/app?packageName=com.ugreen.iot&timestamp=1751608751509' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: b_account_username=v7Wf3wBcfM9BfB8CB0Q6KQ%3D%3D; b_account_aid=s9oXesI7rcg%3D; b_account_token=33172ca3e57108a1c1525bf5e326e7ca.1751090349380; b_account_salt=Hz71UDRV%2BFX4fbJzhXKirg%3D%3D.1751608749380; JSESSIONID=6DB3CBD9BF91844851EB2A62295FDCB0' \
  -H 'Referer: https://dev.vivo.com.cn/comment/tab/appStoreDetails?id=603017&packageName=com.ugreen.iot&appType=1' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'csrfToken: YZRZX0' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'v-source: 0c1726dd402d1d50c417e46e479e6cdc' \
  --compressed"""
    url, headers, data = extract_curl_info(getCore)
    core = requests.get(url, headers=headers, data=data)
    return json.loads(core.text)


if __name__ == '__main__':
    data =getContent()
    print(data)
    data =getCore()
    print(data)

