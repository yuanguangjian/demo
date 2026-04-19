"""Kafka Producer / Consumer demo（合并 `kafka/` 下三个脚本）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import json
import sys

from common.db.kafka import ConfluentConsumer, ConfluentProducer
from common.logger import get_logger

_logger = get_logger(__name__)


def produce_once() -> None:
    producer = ConfluentProducer()
    data = {
        "productModel": "productModel",
        "sn": "sn",
        "region": "region",
        "mac": "mac",
        "version": "version",
        "publicKey": "publicKey",
    }
    producer.send(json.dumps(data))
    producer.flush()


def consume_forever() -> None:
    consumer = ConfluentConsumer()
    consumer.poll_forever(lambda msg: _logger.info("received: %s", msg))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "produce"
    if mode == "produce":
        produce_once()
    else:
        consume_forever()
