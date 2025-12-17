import requests
import time
from datetime import datetime,timezone

print(datetime.now().timestamp())
timestamp = datetime.now(timezone.utc).timestamp()
print(timestamp)
