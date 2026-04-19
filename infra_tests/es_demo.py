"""Elasticsearch 批量写入 demo（原 `ipc项目/es.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import datetime
import random
from typing import Any, Dict, Iterator

from common.db.es import bulk_index
from common.logger import get_logger

_logger = get_logger(__name__)


ES_HOST = "http://192.168.75.132:9200"
INDEX_NAME = "user_ext"
TOTAL_DOCS = 50_000_000
BATCH_SIZE = 5000
START_TIME = datetime.datetime(2011, 8, 9, 1, 42, 30)

SEX_OPTIONS = ["M", "F", "S"]
COUNTRY_CODES = ["CN", "US", "JP", "DE", "FR", "IN"]
DEVICE_BRANDS = ["Apple", "Samsung", "Huawei", "Xiaomi", "Dell"]
DEVICE_TYPES = ["iPhone", "Galaxy", "Mate", "Redmi", "XPS"]


def _generate_doc(i: int) -> Dict[str, Any]:
    create_time = START_TIME + datetime.timedelta(seconds=i * 10)
    update_time = create_time + datetime.timedelta(seconds=random.randint(5, 300))
    birth_date = f"{random.randint(1970, 2010):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    return {
        "_index": INDEX_NAME,
        "_id": i,
        "_source": {
            "user_id": f"user_{i:08d}",
            "nick_name": f"nick_{random.randint(1000, 9999)}",
            "real_name": f"name_{random.randint(1000, 9999)}",
            "sex": random.choice(SEX_OPTIONS),
            "birth_date": birth_date,
            "country_code": random.choice(COUNTRY_CODES),
            "user_regip": ".".join(str(random.randint(0, 255)) for _ in range(4)),
            "pic": "",
            "sign": f"签名_{random.randint(1000, 9999)}",
            "remark": f"备注_{random.randint(1000, 9999)}",
            "device_brand": random.choice(DEVICE_BRANDS),
            "device_type": random.choice(DEVICE_TYPES),
            "source": random.randint(1, 4),
            "env": random.randint(1, 2),
            "create_time": create_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "update_time": update_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        },
    }


def bulk_range(start: int, end: int, *, batch: int = BATCH_SIZE) -> Iterator[int]:
    for i in range(start, end, batch):
        actions = [_generate_doc(k) for k in range(i, min(i + batch, end))]
        ok = bulk_index(ES_HOST, actions)
        _logger.info("%s %s-%s", "OK" if ok else "ERR", i, i + len(actions))
        yield i + len(actions)


if __name__ == "__main__":
    for _ in bulk_range(43_765_000, TOTAL_DOCS):
        pass
