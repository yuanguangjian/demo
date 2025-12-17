import asyncio
import aiofiles
import csv
from gmqtt import Client as MQTTClient
import random

EMQX_HOST = '192.168.75.132'
EMQX_PORT = 1883
DEVICE_TOPIC = '/hello'
MESSAGE = '你好，设备！'
CSV_FILE = 'devices_status1.csv'
CLIENT_COUNT = 10000  # 可根据 CSV 实际数量调整

# 禁用 gmqtt 日志（可选）
import logging
logging.getLogger('gmqtt').setLevel(logging.WARNING)

# 读取 CSV 用户列表
async def load_users():
    users = []
    async with aiofiles.open(CSV_FILE, mode='r', encoding='utf-8') as f:
        content = await f.read()
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            users.append({
                'user_id': row['user_id'],
                'password': row['password']
            })
    return users

# 创建并连接单个客户端
async def connect_client(user):
    client_id = f"client_{user['user_id']}_{random.randint(1000,9999)}"
    client = MQTTClient(client_id)

    client.set_auth_credentials(user['user_id'], user['password'])

    # 可选回调
    client.on_connect = lambda *_: print(f"✅ Connected: {client_id}")
    client.on_disconnect = lambda *_: print(f"❌ Disconnected: {client_id}")

    await client.connect(EMQX_HOST, EMQX_PORT, keepalive=60)
    await asyncio.sleep(1)  # 等待连接稳定
    client.publish(DEVICE_TOPIC, MESSAGE)
    await asyncio.sleep(600)  # 保持在线10分钟

# 主函数：批量连接所有客户端
async def main():
    users = await load_users()
    tasks = [connect_client(user) for user in users[:CLIENT_COUNT]]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
