import re

import requests


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


# 示例 curl 命令
curl_command = """curl 'https://dev.mi.com/uiueapi/comment/usercomment/commentlist?packageName=com.ugreen.iot&limit=8&offset=0&score=&versionName=&startTime=1719849600000&endTime=1744300800000&model=&searchKeyWords=&mideveloper_ph=ZPs5CqduH0FQKS0tEzZiLA%3D%3D&userId=2549403030' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: uLocale=zh_CN; pageType=1; openPlatform=0; JSESSIONID=aaayhEC4mCX2xg5jJjFyz; serviceToken=Xv5lATucFWfMVEEue0csFNqGfoD91Gto82m5gFu3HK0COBJCGjp2qpD/5rLYAQBFPkj5IX5YkjJs84AKKR6ze1odFO04rAi/yXuuHeFXXZfnpJb0Qx9KMPCeh8iIatERuwKxjevW336g4jRnwEzkk7/WdhsCasNh5+xTTltBm6zRa8M3eIgRTMpW1dXq3WPGIVFcStI6oZ7OgDDh69qDuWUF8rg/rupKVYdHP8yyTGuOjv6SowwUzOqj24iIla0mZL+S+E9m9wwVOGp2E8MSfNLrbjS/6q2CpKjcEx9LUyRCWGybAF9uezNEmwb2z+M5s2RHg5guvJCFkSW5PD4O/vWuatS+6Ft6PVbdkY/BCQw=; userId=2549403030; mideveloper_slh=eyu+SF03d+dGGFAS1VMxLbzDsIk=; mideveloper_ph=ZPs5CqduH0FQKS0tEzZiLA==; ABtestWhiteUser=1; certification=%E6%B7%B1%E5%9C%B3%E5%B8%82%E7%BB%BF%E8%81%94%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; canSwitch=0; currentSite=1; self_developer_id=1060664; self_developer_type=2; developer_id=1060664; developer_type=2; devname=%E6%B7%B1%E5%9C%B3%E5%B8%82%E7%BB%BF%E8%81%94%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; openGrayApp=0; route=b307c054bfc1cae57687cbd83ee54c66' \
  -H 'Referer: https://dev.mi.com/distribute/app/2882303761520310413/comment?packageName=com.ugreen.iot&namespaceValue=0&userId=2549403030' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'traceparent: 00-0978dca0c28556e6eea94fb5d8c8b9df-c74db9d66fab3fd0-01' \
  -H 'x-developer-gray: main' \
  -H 'x-package-name: com.ugreen.iot' \
  --compressed"""

# 调用方法并打印结果
url, headers, data = extract_curl_info(curl_command)
print("URL:", url)
print("Headers:", headers)
print("Data:", data)

response = requests.get(url, headers=headers, data=data)
print(response.text)
