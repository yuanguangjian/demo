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
    getContent = """curl 'https://agc-drcn.developer.huawei.com/agc/edge/review/v1/manage/developer/reviews/query?entityId=110890551&entityType=1&limit=50&page=1&sort=0&startTime=1743782400000&endTime=1751644799000' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: CASLOGINSITE=1; LOGINACCSITE=1; HuaweiID_CAS_ISCASLOGIN=true; X-HD-SESSION=f38c077f-63ac-95d7-e0c2-c2cf7b8ffc83; authInfo="{\"accesstoken\":\"DQEAACQvyAoRzq1hl6qg0NbtdmC867O8hpFftGY6Xac7v8ZuMlEvLOpTQsDFd36s8NZe5blJCAXKiYBkx4vNyyPwJmotFBbIqJNTgy35g2ztiBIOxCOYe1ZkXe9u2NaTqkpliSR2yA==\",\"createtime\":\"20250704T060155Z\",\"expiretime\":\"20250704T070155Z\",\"rtCiphertext\":\"crjvZnG3HFiJrJ/WmZCg/NQwjpUbIIGGM07eG6NLtS5oS+gmenao6msj0hD2dPeBMnQO5tdZKh4rkeyUCMbYnCd2087KgWVtpNxe4wfN/Nuh/7537yRf4XiGWDSOCPKLm0p/SymKYWyOcg/ckEoA7Z4KZ4kL2S3qw3HV9/1/XxZzCHNHSJ0v7FlV3PrD+QB8UPCAZEsHAOXzYhWcWE8CCA==\",\"signature\":\"642dfa182b5164c7896248be527d5c85e100c0d7e65ff33087983a8901807319\",\"siteID\":\"1\"}"; authdata="{\"accesstoken\":\"TlCEAGKCxFmotYXF8jMtyZwZ7TuINHoh0HDUBscvpwL3I+jAL37cp63L4Osg/aQiOsGv289NX9Jz343IeIEnif7p0xA4MhNDTClnMNaX89Xv0E2gSE2PAQ5hjeeS76oE7/BXAxR6mQ8hCn3forVP2Vru0i1tlgoQs02mUXTw/t4ZYiAHsD+T6gu8tX5HWUhnNupGwe7EWToKfIrApDNtDQ==\",\"createtime\":\"20250704T060155Z\",\"expiretime\":\"20250704T070155Z\",\"loginTime\":\"20250704T060155Z\",\"rtCiphertext\":\"8i3YHQoTJ9bCzPguRO21zTAHdS7Bo4BAxr3APYRpnOFmIEAa9/Z8g4rXaEtJa+HrKxB3nzUUuoB/9FuZYN+0ve9xFtIzDi35vTWn7TZoKf63JLscwtBtf/1pTpH96+JL+iwy5UKjZUvOSAlXNRcOgr8V0FkRX2SySdzPYw/fnirB0uzenFsGXnUDddu01SESF1/PFbpNcMpf+5Gcn85X2Q==\",\"signature\":\"920b62af26b0083f86ddc70623c7b380bc485f9db3f411f4e8b3ba2d571d7572\",\"siteID\":\"1\"}"; csrfToken=4201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C; x-siteId=1; developer_userinfo=%7B%22siteid%22%3A%221%22%2C%22expiretime%22%3A%2220250704T070155Z%22%2C%22csrftoken%22%3A%224201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C%22%2C%22teamid%22%3A%22890086200300034431%22%7D; x-teamId=890086200300034431; x-userType=2; x-country=CN; HWWAFSESTIME=1751608928755; HWWAFSESID=11ff27621ef09b50e2; x-hd-grey=alnc-000_agcGreyFlag-0_agcTeamId-890086200300034431' \
  -H 'Origin: https://developer.huawei.com' \
  -H 'Referer: https://developer.huawei.com/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-HD-CSRF: 4201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C' \
  -H 'agcTeamId: 890086200300034431' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw '{"auditStates":[1,3],"countries":["CN"]}' \
  --compressed"""
    url, headers, data = extract_curl_info(getContent)
    content = requests.post(url, headers=headers, data=data)
    return json.loads(content.text)


def getCore():
    getCore = """curl 'https://agc-drcn.developer.huawei.com/agc/edge/review/v1/manage/developer/ratingStat?entityId=110890551&entityType=1' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: CASLOGINSITE=1; LOGINACCSITE=1; HuaweiID_CAS_ISCASLOGIN=true; X-HD-SESSION=f38c077f-63ac-95d7-e0c2-c2cf7b8ffc83; authInfo="{\"accesstoken\":\"DQEAACQvyAoRzq1hl6qg0NbtdmC867O8hpFftGY6Xac7v8ZuMlEvLOpTQsDFd36s8NZe5blJCAXKiYBkx4vNyyPwJmotFBbIqJNTgy35g2ztiBIOxCOYe1ZkXe9u2NaTqkpliSR2yA==\",\"createtime\":\"20250704T060155Z\",\"expiretime\":\"20250704T070155Z\",\"rtCiphertext\":\"crjvZnG3HFiJrJ/WmZCg/NQwjpUbIIGGM07eG6NLtS5oS+gmenao6msj0hD2dPeBMnQO5tdZKh4rkeyUCMbYnCd2087KgWVtpNxe4wfN/Nuh/7537yRf4XiGWDSOCPKLm0p/SymKYWyOcg/ckEoA7Z4KZ4kL2S3qw3HV9/1/XxZzCHNHSJ0v7FlV3PrD+QB8UPCAZEsHAOXzYhWcWE8CCA==\",\"signature\":\"642dfa182b5164c7896248be527d5c85e100c0d7e65ff33087983a8901807319\",\"siteID\":\"1\"}"; authdata="{\"accesstoken\":\"TlCEAGKCxFmotYXF8jMtyZwZ7TuINHoh0HDUBscvpwL3I+jAL37cp63L4Osg/aQiOsGv289NX9Jz343IeIEnif7p0xA4MhNDTClnMNaX89Xv0E2gSE2PAQ5hjeeS76oE7/BXAxR6mQ8hCn3forVP2Vru0i1tlgoQs02mUXTw/t4ZYiAHsD+T6gu8tX5HWUhnNupGwe7EWToKfIrApDNtDQ==\",\"createtime\":\"20250704T060155Z\",\"expiretime\":\"20250704T070155Z\",\"loginTime\":\"20250704T060155Z\",\"rtCiphertext\":\"8i3YHQoTJ9bCzPguRO21zTAHdS7Bo4BAxr3APYRpnOFmIEAa9/Z8g4rXaEtJa+HrKxB3nzUUuoB/9FuZYN+0ve9xFtIzDi35vTWn7TZoKf63JLscwtBtf/1pTpH96+JL+iwy5UKjZUvOSAlXNRcOgr8V0FkRX2SySdzPYw/fnirB0uzenFsGXnUDddu01SESF1/PFbpNcMpf+5Gcn85X2Q==\",\"signature\":\"920b62af26b0083f86ddc70623c7b380bc485f9db3f411f4e8b3ba2d571d7572\",\"siteID\":\"1\"}"; csrfToken=4201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C; x-siteId=1; developer_userinfo=%7B%22siteid%22%3A%221%22%2C%22expiretime%22%3A%2220250704T070155Z%22%2C%22csrftoken%22%3A%224201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C%22%2C%22teamid%22%3A%22890086200300034431%22%7D; x-teamId=890086200300034431; x-userType=2; x-country=CN; HWWAFSESTIME=1751608928755; HWWAFSESID=11ff27621ef09b50e2; x-hd-grey=alnc-000_agcGreyFlag-0_agcTeamId-890086200300034431' \
  -H 'Origin: https://developer.huawei.com' \
  -H 'Referer: https://developer.huawei.com/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-HD-CSRF: 4201ABF027B6C73EE0617008766F22CDC6475CD774D522FA2C' \
  -H 'agcTeamId: 890086200300034431' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --compressed"""
    url, headers, data = extract_curl_info(getCore)
    core = requests.get(url, headers=headers, data=data)
    return json.loads(core.text)


if __name__ == '__main__':
    data =getContent()
    print(data)
    data =getCore()
    print(data)

