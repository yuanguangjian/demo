from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer
import time

# Kafka 配置
BOOTSTRAP_SERVERS = "192.168.75.132:9092"
TOPIC_NAME = "hello"

# 创建 Topic（如果不存在）
def create_topic():
    admin_client = KafkaAdminClient(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        client_id="topic_creator"
    )
    topic = NewTopic(name=TOPIC_NAME, num_partitions=1, replication_factor=1)
    try:
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        print(f"[✓] Topic '{TOPIC_NAME}' created.")
    except Exception as e:
        print(f"[!] Topic creation skipped or failed: {e}")

# 发送消息
def send_message(message):
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: v.encode("utf-8")
    )
    producer.send(TOPIC_NAME, value=message)
    producer.flush()
    print(f"[→] Sent: {message}")

# 接收消息（只接收一条）
def receive_message():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="demo-group",
        value_deserializer=lambda x: x.decode("utf-8")
    )
    print("[←] Waiting for message...")
    for msg in consumer:
        print(f"[✓] Received: {msg.value}")
        # break

# 主流程
if __name__ == "__main__":
    # create_topic()
    # time.sleep(1)  # 等待 Kafka 同步
    # send_message("你好，Kafka！")
    time.sleep(1)  # 等待消息写入
    receive_message()
