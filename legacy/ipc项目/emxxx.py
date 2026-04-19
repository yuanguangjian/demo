import requests
import base64

if __name__ == '__main__':
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "basic "+base64.b64encode(b"ee26b0dd4af7e749:e2BZ3nGh9C9CkAWzO9C9AtSuJKNdrGQyn9BJ5p7YUURXr2nC").decode()
    }
    result = requests.get("http://192.168.75.132:18083/api/v5/clients",headers=headers)
    print(result.text)