import json

from confluent_kafka import Producer
import setting

conf = setting.kafka_setting
"""初始化一个 Producer 对象"""
p = Producer({'bootstrap.servers': conf['bootstrap_servers']})

data = {
    "productModel": "productModel",
    "sn": "sn",
    "region": "region",
    "mac": "mac",
    "version": "version",
    "publicKey": "publicKey",
}


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


"""异步发送消息"""
print(f"发送数据是：{json.dumps(data)}")
p.produce(conf['topic_name'], json.dumps(data).encode("utf-8"), callback=delivery_report)
p.poll(0)
"""在程序结束时，调用flush"""
p.flush()
