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
    getContent = """curl 'https://dev.mi.com/uiueapi/comment/usercomment/commentlist?packageName=com.ugreen.iot&limit=8&offset=0&score=&versionName=&startTime=1748966400000&endTime=1751558400000&model=&searchKeyWords=&mideveloper_ph=d%2F6SAg0NhUqV4Bc21bJaMg%3D%3D&userId=2549403030' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: uLocale=zh_CN; pageType=1; openPlatform=0; JSESSIONID=aaa1tTYQ6fFrwblSKqoFz; serviceToken=Xv5lATucFWfMVEEue0csFBQ87B9/XpWSb/2dNk1mHlEJzjIZujS6kMTyMkikEuJLyBC0RMO8qV8YDyOzA7EporKg0hchiHB5a+EX6td/CH0xbFopFIxa2m7s70QxCDkH9TC4NbSqTG260CM9acb8X3ltNKd+STu6I6u/ngigSSkG5pbqfETHdFWAEFxJ34vtfZalZhLErAfbhCF46QJuh+HRI3i1S9wLfExQp6YGqzameAQVWJSQV6j5hPfaUAlVyAOe/+1RdPiV6VwPf2ujlNFabLIo3uO4LJbPDrdZ+kkBjZXWEQ3by0PcQnTkgbXo13YVnzwh3GxpM6QRK3qG/Gs940mU0dAUZu+DBejAQuw=; userId=2549403030; mideveloper_slh=X7hf5etxGuI/fIz99rcF2n1q24o=; mideveloper_ph=d/6SAg0NhUqV4Bc21bJaMg==; ABtestWhiteUser=1; certification=%E6%B7%B1%E5%9C%B3%E5%B8%82%E7%BB%BF%E8%81%94%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; canSwitch=0; currentSite=1; self_developer_id=1060664; self_developer_type=2; developer_id=1060664; developer_type=2; devname=%E6%B7%B1%E5%9C%B3%E5%B8%82%E7%BB%BF%E8%81%94%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; openGrayApp=1; route=4709bc338c3caf8869e0bb7b0db1978b' \
  -H 'Referer: https://dev.mi.com/distribute/app/2882303761520310413/comment?packageName=com.ugreen.iot&namespaceValue=0&userId=2549403030' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'traceparent: 00-acd2630966ad9501693d0e6d5a6a0e59-097909a3f7cf3a3c-01' \
  -H 'x-developer-gray: main' \
  -H 'x-package-name: com.ugreen.iot' \
  --compressed"""
    url, headers, data = extract_curl_info(getContent)
    content = requests.get(url, headers=headers, data=data)
    return json.loads(content.text)


def getCore():
    getCore = """curl 'https://dev.mi.com/uiueapi/comment/usercomment/scores?packageName=com.ugreen.iot&mideveloper_ph=d%2F6SAg0NhUqV4Bc21bJaMg%3D%3D&userId=2549403030' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: uLocale=zh_CN; pageType=1; openPlatform=0; JSESSIONID=aaa1tTYQ6fFrwblSKqoFz; serviceToken=Xv5lATucFWfMVEEue0csFBQ87B9/XpWSb/2dNk1mHlEJzjIZujS6kMTyMkikEuJLyBC0RMO8qV8YDyOzA7EporKg0hchiHB5a+EX6td/CH0xbFopFIxa2m7s70QxCDkH9TC4NbSqTG260CM9acb8X3ltNKd+STu6I6u/ngigSSkG5pbqfETHdFWAEFxJ34vtfZalZhLErAfbhCF46QJuh+HRI3i1S9wLfExQp6YGqzameAQVWJSQV6j5hPfaUAlVyAOe/+1RdPiV6VwPf2ujlNFabLIo3uO4LJbPDrdZ+kkBjZXWEQ3by0PcQnTkgbXo13YVnzwh3GxpM6QRK3qG/Gs940mU0dAUZu+DBejAQuw=; userId=2549403030; mideveloper_slh=X7hf5etxGuI/fIz99rcF2n1q24o=; mideveloper_ph=d/6SAg0NhUqV4Bc21bJaMg==; ABtestWhiteUser=1; certification=%E6%B7%B1%E5%9C%B3%E5%B8%82%E7%BB%BF%E8%81%94%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; canSwitch=0; currentSite=1; self_developer_id=1060664; self_developer_type=2; developer_id=1060664; developer_type=2; devname=%E6%B7%B1%E5%9C%B3%E5%B8%82%E7%BB%BF%E8%81%94%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; openGrayApp=0; route=b307c054bfc1cae57687cbd83ee54c66' \
  -H 'Referer: https://dev.mi.com/distribute/app/2882303761520310413/comment?packageName=com.ugreen.iot&namespaceValue=0&userId=2549403030' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'traceparent: 00-56a46c3b88d611d9313f1f34608c8bed-de723b238d331bf7-01' \
  -H 'x-developer-gray: main' \
  -H 'x-package-name: com.ugreen.iot' \
  --compressed"""
    url, headers, data = extract_curl_info(getCore)
    core = requests.get(url, headers=headers, data=data)
    return json.loads(core.text)


if __name__ == '__main__':
    data =getContent()
    print(data)
    data =getCore()
    print(data)

