import csv
import time
import threading
import paho.mqtt.client as mqtt

# EMQX Broker 配置
EMQX_HOST = "192.168.75.132"
EMQX_PORT = 1883
DEVICE_TOPIC = "/hello"
MESSAGE = "你好，设备！"

# 从 CSV 文件读取账号密码
users = []
with open("devices_status.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        users.append({
            "user_id": row["user_id"],
            "password": row["password"]
        })

# 连接成功回调
def on_connect(client, userdata, flags, rc):
    user_id = userdata["user_id"]
    print(f"[{user_id}] 连接结果: {mqtt.connack_string(rc)}")


# 为每个用户创建独立连接
def connect_and_publish(user):
    client_id = f"client_{user['user_id']}"
    client = mqtt.Client(client_id=client_id, userdata={"user_id": user["user_id"]})
    client.username_pw_set(user["user_id"], user["password"])
    client.on_connect = on_connect
    client.connect(EMQX_HOST, EMQX_PORT, keepalive=60)
    client.loop_start()
    time.sleep(1)  # 等待连接和发送完成
    client.loop_stop()
    client.disconnect()

# 多线程并发连接
threads = []
for user in users:
    t = threading.Thread(target=connect_and_publish, args=(user,))
    threads.append(t)
    t.start()
    time.sleep(0.01)  # 控制连接速率

# 等待所有线程完成
for t in threads:
    t.join()

print("所有消息已发送完毕。")
