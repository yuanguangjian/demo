import requests
import time


result  = requests.get("https://dev3.ugreeniot.com/metadata/v1/factory/getSn?mac=BC:AD:AE:C8:17:E7")
print(result.text)

