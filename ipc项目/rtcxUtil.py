import hashlib
import hmac
import base64
import json
import uuid
import time
from datetime import datetime, timezone
from collections import OrderedDict
import requests


def get_gmt_date(timestamp_ms):
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


def content_md5(body_bytes):
    md5_digest = hashlib.md5(body_bytes).digest()
    base64_md5 = base64.b64encode(md5_digest).decode('utf-8')
    return base64_md5[:23] if len(base64_md5) > 24 else base64_md5


def headers_str(headers, signature_headers):
    sb = []
    sorted_headers = OrderedDict()
    if signature_headers:
        for key in signature_headers.split(','):
            sorted_headers[key] = headers.get(key, '')
    else:
        sorted_headers.update(headers)

    for k, v in sorted(sorted_headers.items()):
        if not k.lower().startswith('x-ca') or k.lower() in ['x-ca-signature-headers', 'x-ca-signature']:
            continue
        sb.append(f"{k.strip().lower()}:{v.strip() if v else ''}")
    return '\n'.join(sb) + ''


def build_string_to_sign(method, headers, uri, body_bytes):
    accept = headers.get('Accept', '\n')
    content_type = headers.get('Content-Type', '\n')
    date = headers.get('date') or headers.get('Date', '\n')
    signature_headers = headers.get('x-ca-signature-headers', '')

    parts = [
        method.upper(),
        accept,
        content_md5(body_bytes),
        content_type,
        date,
        headers_str(headers, signature_headers),
        uri
    ]
    return '\n'.join(parts)


def sign(method, secret, headers, uri, body_bytes):
    string_to_sign = build_string_to_sign(method, headers, uri, body_bytes)
    hmac_sha256 = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(hmac_sha256.digest()).decode('utf-8')


def handler(path, body_dict):
    # 构造 headers
    app_key = 'PdRWfv0XaeJulQLKPh9GXo4P1'
    app_secret = 'xyJtvem4l1eaqh8Cy17i1AsGAEUaD6d'
    method = 'POST'
    timestamp = int(time.time() * 1000)
    headers = {
        'x-ca-key': app_key,
        'x-ca-timestamp': str(timestamp),
        'x-ca-nonce': str(uuid.uuid4()),
        'Date': get_gmt_date(timestamp),
        'Accept': 'application/json; charset=utf-8',
        'Content-Type': 'application/octet-stream; charset=utf-8',
        'x-ca-signature-headers': 'x-ca-key,x-ca-nonce,x-ca-timestamp'
    }
    body_str = json.dumps(body_dict, separators=(',', ':'))
    body_bytes = body_str.encode('utf-8')
    signature = sign(method, app_secret, headers, path, body_bytes)
    headers['x-ca-signature'] = signature
    url = 'https://third-gateway.iotrtc.cn' + path
    response = requests.post(url, headers=headers, data=body_str)
    return response.text


def getToken():
    data = {
        "id": str(uuid.uuid4()),
        "params": {},
        "request": {
            "apiVer": "1.0.0"
        },
        "version": "1.0"
    }
    path = '/platform/cloud/token'
    result = handler(path, data)
    json_result = json.loads(result)
    return json_result["data"]["accessToken"]


def request(path, body_dict):
    token = getToken()
    body_dict["request"]["cloudToken"] = token
    return handler(path,body_dict)


if __name__ == '__main__':
    getToken()
