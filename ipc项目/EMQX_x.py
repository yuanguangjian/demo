import json
import time
import threading
import paho.mqtt.client as mqtt

# EMQX Broker 配置
EMQX_HOST = "192.168.75.132"
EMQX_PORT = 1883
PASSWORD = "Aa123456"
DEVICE_TOPIC = "/hello"
MESSAGE = "你好，设备！"

# 从 JSON 文件读取用户名列表
with open("users.json", "r", encoding="utf-8") as f:
    usernames = json.load(f)

# 连接成功回调
def on_connect(client, userdata, flags, rc):
    username = userdata["username"]
    print(f"[{username}] 连接结果: {mqtt.connack_string(rc)}")
    if rc == 0:
        print(f"[{username}] 连接成功，发送消息...")
        # for i in range(100):
        #     client.publish(DEVICE_TOPIC, f"{MESSAGE} - 来自 {username}-{i}", qos=1)
    else:
        print(f"[{username}] 连接失败")

# 为每个用户创建独立连接
def connect_and_publish(username):
    client = mqtt.Client(client_id=f"client_{username}", userdata={"username": username})
    client.username_pw_set(username, PASSWORD)
    client.on_connect = on_connect
    client.connect(EMQX_HOST, EMQX_PORT, keepalive=60)
    client.loop_start()
    time.sleep(3000)  # 等待连接和发送完成
    client.loop_stop()
    client.disconnect()

# 多线程并发连接
threads = []
for username in usernames:
    t = threading.Thread(target=connect_and_publish, args=(username,))
    threads.append(t)
    t.start()

# 等待所有线程完成
for t in threads:
    t.join()

print("所有消息已发送完毕。")
