import requests
import json
import random
import datetime

# Elasticsearch 配置
ES_HOST = "http://192.168.75.132:9200"
INDEX_NAME = "user_ext"
TOTAL_DOCS = 50000000  # 可改为 50000000
BATCH_SIZE = 5000

# 起始时间
START_TIME = datetime.datetime(2011, 8, 9, 1, 42, 30)

# 字段选项
SEX_OPTIONS = ["M", "F", "S"]
COUNTRY_CODES = ["CN", "US", "JP", "DE", "FR", "IN"]
DEVICE_BRANDS = ["Apple", "Samsung", "Huawei", "Xiaomi", "Dell"]
DEVICE_TYPES = ["iPhone", "Galaxy", "Mate", "Redmi", "XPS"]

# 时间生成函数
def generate_time(i):
    create_time = START_TIME + datetime.timedelta(seconds=i * 10)
    update_time = create_time + datetime.timedelta(seconds=random.randint(5, 300))
    create_str = create_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    update_str = update_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return create_str, update_str

# 构造文档
def generate_doc(i):
    create_time, update_time = generate_time(i)
    birth_date = f"{random.randint(1970, 2010):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
    return {
        "_index": INDEX_NAME,
        "_id": i,
        "_source": {
            "user_id": f"user_{i:08d}",
            "nick_name": f"nick_{random.randint(1000,9999)}",
            "real_name": f"name_{random.randint(1000,9999)}",
            "sex": random.choice(SEX_OPTIONS),
            "birth_date": birth_date,
            "country_code": random.choice(COUNTRY_CODES),
            "user_regip": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            "pic": "",
            "sign": f"签名_{random.randint(1000,9999)}",
            "remark": f"备注_{random.randint(1000,9999)}",
            "device_brand": random.choice(DEVICE_BRANDS),
            "device_type": random.choice(DEVICE_TYPES),
            "source": random.randint(1, 4),
            "env": random.randint(1, 2),
            "create_time": create_time,
            "update_time": update_time
        }
    }

# 构造 NDJSON 格式 payload
def build_bulk_payload(actions):
    lines = []
    for action in actions:
        meta = { "index": { "_index": action["_index"], "_id": action["_id"] } }
        source = action["_source"]
        lines.append(json.dumps(meta))
        lines.append(json.dumps(source))
    return "\n".join(lines) + "\n"

# 批量插入
for start in range(43765000, TOTAL_DOCS, BATCH_SIZE):
    end = min(start + BATCH_SIZE, TOTAL_DOCS)
    actions = [generate_doc(i) for i in range(start, end)]
    payload = build_bulk_payload(actions)
    headers = {"Content-Type": "application/x-ndjson"}
    res = requests.post(f"{ES_HOST}/_bulk", headers=headers, data=payload)
    if res.status_code < 300:
        print(f"✅ Inserted documents {start} to {end}")
    else:
        print(f"❌ Error inserting documents {start} to {end}: {res.status_code}")
        print(res.text)

