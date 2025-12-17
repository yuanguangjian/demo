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
    getContent = """curl 'https://open.oppomobile.com/resource/comment/list.json' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'Cookie: firstLoginTokenForTT=true; _dx_captcha_vid=; _dx_uzZo5y=996389466c995bba4c8bc3df54a60075920c53ae62931fea79e051ca7be6b6e7c02a6eed; sdkLoginToken=true; www.echatsoft.com_418_encryptVID=NrFAsdcJLJ8D6JXnufcYSA%3D%3D; www.echatsoft.com_418_chatVisitorId=4477248386; echat_firsturl=--1; echat_firsttitle=--1; echat_referrer_timer=echat_referrer_timeout; echat_referrer=--1; echat_referrer_pre=; ECHAT_418_web4477248386_miniHide=0; opkey=eyJpdiI6ImQrQzZYL1B5WlhCNktxNjRuQU5yRVE9PSIsIm1hYyI6IiIsInZhbHVlIjoiSS80TmFKYzYvRFhXbzczQmZUc0plcEhaVERYaXduYmZiSFM3a1dmYVMrNEtybXZkNUZoZ1I4Y0ZoVU5xZk14aUp3b04vMDBwcDNrTEJDbFhwOU9EZ2dodlRmMit5SmFHQmk1aXNpS0hLcitpRWI2c0l4S0JaRXo0SUZUNldkV3EifQ%3D%3D; isLogin=1; openplatGray=gray; openplatIsGray=1; openplatService=settlement; openplat=084c0de69023686549ebd51c4717a97f; OPPOSID=K-3OTVD8UC1kZGnpwIaFRjTlnJfXWLjD7rBnOdnCe_8GwVgmX7ZOWlJ5FW1CHFVdkEEUw-xYRYM; STORE_USERNAME=%E7%94%A8%E6%88%B701705198545; dev_id=794874914; OPENPLATLOGIN=1; _dx_app_ef635f04cfca5b0bece59d8f92ccf2bb=68676e223gD6jxq9WQ3MnrmfxIZnPvD9tVbxQjW1; obus-track_20293_session=LsNJB2wl,1751608785854,1751608823766; cloudObservationRumSessionId=556b1b03199562b745d7d90b88ee8aa0-1751608824087-commonfrontend' \
  -H 'Origin: https://open.oppomobile.com' \
  -H 'Referer: https://open.oppomobile.com/home/management/app-admin' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'traceparent: 00-acc7ed4961c91a477640f189e8256abe-d610ac7872280e43-00' \
  --data-raw 'page=1&app_id=31704887&level=0&content=&from_datetime=&to_datetime=&cp_order=&cp_sort=&replied=' \
  --compressed"""
    url, headers, data = extract_curl_info(getContent)
    content = requests.post(url, headers=headers, data=data)
    return json.loads(content.text)


def getCore():
    getCore = """curl 'https://open.oppomobile.com/resource/comment/index.json' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'Cookie: firstLoginTokenForTT=true; _dx_captcha_vid=; _dx_uzZo5y=996389466c995bba4c8bc3df54a60075920c53ae62931fea79e051ca7be6b6e7c02a6eed; sdkLoginToken=true; www.echatsoft.com_418_encryptVID=NrFAsdcJLJ8D6JXnufcYSA%3D%3D; www.echatsoft.com_418_chatVisitorId=4477248386; echat_firsturl=--1; echat_firsttitle=--1; echat_referrer_timer=echat_referrer_timeout; echat_referrer=--1; echat_referrer_pre=; ECHAT_418_web4477248386_miniHide=0; opkey=eyJpdiI6ImQrQzZYL1B5WlhCNktxNjRuQU5yRVE9PSIsIm1hYyI6IiIsInZhbHVlIjoiSS80TmFKYzYvRFhXbzczQmZUc0plcEhaVERYaXduYmZiSFM3a1dmYVMrNEtybXZkNUZoZ1I4Y0ZoVU5xZk14aUp3b04vMDBwcDNrTEJDbFhwOU9EZ2dodlRmMit5SmFHQmk1aXNpS0hLcitpRWI2c0l4S0JaRXo0SUZUNldkV3EifQ%3D%3D; isLogin=1; openplatGray=gray; openplatIsGray=1; openplatService=settlement; openplat=084c0de69023686549ebd51c4717a97f; OPPOSID=K-3OTVD8UC1kZGnpwIaFRjTlnJfXWLjD7rBnOdnCe_8GwVgmX7ZOWlJ5FW1CHFVdkEEUw-xYRYM; STORE_USERNAME=%E7%94%A8%E6%88%B701705198545; dev_id=794874914; OPENPLATLOGIN=1; _dx_app_ef635f04cfca5b0bece59d8f92ccf2bb=68676e223gD6jxq9WQ3MnrmfxIZnPvD9tVbxQjW1; obus-track_20293_session=LsNJB2wl,1751608785854,1751608823766; cloudObservationRumSessionId=556b1b03199562b745d7d90b88ee8aa0-1751608824087-commonfrontend' \
  -H 'Origin: https://open.oppomobile.com' \
  -H 'Referer: https://open.oppomobile.com/home/management/app-admin' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'sec-ch-ua: "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'traceparent: 00-2470d97e388c5ccaf688dcfa22781e85-eebe18dbc0a47a30-00' \
  --data-raw 'app_id=31704887' \
  --compressed"""
    url, headers, data = extract_curl_info(getCore)
    core = requests.post(url, headers=headers, data=data)
    return json.loads(core.text)


if __name__ == '__main__':
    data =getContent()
    print(data)
    data =getCore()
    print(data)

