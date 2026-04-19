"""Kafka 客户端：基于 `confluent-kafka` 与 `kafka-python` 的薄封装。

同时保留两套实现：
- `ConfluentProducer/ConfluentConsumer`：原 `demo/kafka/` 使用。
- `create_topic`/`send_message`/`consume`：原 `ipc项目/kafka_test.py` 使用。

配置来源：`kafka.json`，缺失时回退到历史硬编码（192.168.75.132:9092）。
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional

from ..config import load_json
from ..logger import get_logger

_logger = get_logger(__name__)

_FALLBACK_SETTING: Dict[str, Any] = {
    "bootstrap_servers": "192.168.75.132:9092",
    "topic_name": "topic_hello",
    "group_name": "group_hello",
}


def get_setting() -> Dict[str, Any]:
    return load_json("kafka.json") or _FALLBACK_SETTING


class ConfluentProducer:
    """基于 confluent-kafka 的简单 Producer。"""

    def __init__(self, setting: Optional[Dict[str, Any]] = None) -> None:
        from confluent_kafka import Producer

        cfg = setting or get_setting()
        self.topic = cfg["topic_name"]
        self._producer = Producer({"bootstrap.servers": cfg["bootstrap_servers"]})

    @staticmethod
    def _delivery(err: Any, msg: Any) -> None:
        if err is not None:
            _logger.error("消息投递失败: %s", err)
        else:
            _logger.info("已投递到 %s [%s]", msg.topic(), msg.partition())

    def send(self, data: Any, topic: Optional[str] = None) -> None:
        payload = json.dumps(data).encode("utf-8") if not isinstance(data, (bytes, bytearray)) else data
        self._producer.produce(topic or self.topic, payload, callback=self._delivery)
        self._producer.poll(0)

    def flush(self) -> None:
        self._producer.flush()


class ConfluentConsumer:
    """基于 confluent-kafka 的简单 Consumer（阻塞轮询）。"""

    def __init__(self, setting: Optional[Dict[str, Any]] = None) -> None:
        from confluent_kafka import Consumer

        cfg = setting or get_setting()
        self.topic = cfg["topic_name"]
        self._consumer = Consumer(
            {
                "bootstrap.servers": cfg["bootstrap_servers"],
                "group.id": cfg["group_name"],
                "auto.offset.reset": "latest",
            }
        )
        self._consumer.subscribe([self.topic])

    def poll_forever(self, handler: Callable[[str], None]) -> None:
        from confluent_kafka import KafkaError

        try:
            while True:
                msg = self._consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    _logger.warning("Consumer 错误: %s", msg.error())
                    continue
                handler(msg.value().decode("utf-8"))
        finally:
            self._consumer.close()


# -- kafka-python 版（用于 create topic / admin 等能力） --
def create_topic(topic: str, *, bootstrap_servers: str, num_partitions: int = 1, replication: int = 1) -> None:
    from kafka.admin import KafkaAdminClient, NewTopic

    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="topic_creator")
    try:
        admin.create_topics([NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication)])
        _logger.info("topic '%s' 已创建", topic)
    except Exception as exc:
        _logger.warning("topic '%s' 创建跳过或失败: %s", topic, exc)


def send_via_kafka_python(topic: str, message: str, *, bootstrap_servers: str) -> None:
    from kafka import KafkaProducer

    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: v.encode("utf-8"),
    )
    producer.send(topic, value=message)
    producer.flush()
    _logger.info("已发送: %s", message)


def consume_via_kafka_python(
    topic: str,
    *,
    bootstrap_servers: str,
    group_id: str = "demo-group",
    one_shot: bool = False,
) -> None:
    from kafka import KafkaConsumer

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: x.decode("utf-8"),
    )
    _logger.info("等待消息...")
    for msg in consumer:
        _logger.info("收到: %s", msg.value)
        if one_shot:
            break
