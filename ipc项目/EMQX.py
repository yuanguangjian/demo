import asyncio
import aiofiles
import csv
from gmqtt import Client as MQTTClient
import random
import logging
import sys


# 📡 EMQX 配置
EMQX_HOST = '192.168.75.132'
EMQX_PORT = 1883
DEVICE_TOPIC = '/hello'
MESSAGE = 'HELLO'
CSV_FILE = 'devices_status1.csv'
KEEP_ALIVE_SECONDS = 1200  # 每个连接保持在线 20 分钟
BATCH_SIZE = 10          # 每秒启动 100 个连接

# 🔕 禁用 gmqtt 日志（可选）
logging.getLogger('gmqtt').setLevel(logging.WARNING)

# 📄 读取 CSV 用户列表
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

# 🔐 单个客户端连接任务（带限速控制）
async def connect_client_with_semaphore(user, semaphore):
    async with semaphore:
        await connect_client(user)

# 🚀 创建并连接单个客户端
async def connect_client(user):
    client_id = f"client_{user['user_id']}_{random.randint(1000,9999)}"
    client = MQTTClient(client_id)
    client.set_auth_credentials(user['user_id'], user['password'])

    client.on_connect = lambda *_: client.publish(DEVICE_TOPIC, MESSAGE)
    client.on_disconnect = lambda client, packet, exc=None: print(f"❌ Disconnected: {client._client_id} Reason: {exc}")

    try:
        await asyncio.wait_for(client.connect(EMQX_HOST, EMQX_PORT, keepalive=60), timeout=50)
        await asyncio.sleep(KEEP_ALIVE_SECONDS)
    except asyncio.TimeoutError:
        print(f"⏱️ {client_id} 连接超时")
    except Exception as e:
        print(f"⚠️ {client_id} 异常: {e}")

# 🧠 主函数：分批启动连接任务
async def main():
    users = await load_users()
    total = len(users)
    print(f"📦 总用户数: {total}")

    semaphore = asyncio.Semaphore(1000)  # 控制最大并发连接数
    all_tasks = []

    for i in range(0, total, BATCH_SIZE):
        batch = users[i:i + BATCH_SIZE]
        tasks = [asyncio.create_task(connect_client_with_semaphore(user, semaphore)) for user in batch]
        all_tasks.extend(tasks)
        print(f"🚀 启动第 {i // BATCH_SIZE + 1} 批，共 {len(batch)} 个连接")
        await asyncio.sleep(1)  # 每秒启动一批

    await asyncio.gather(*all_tasks)

# 🏁 启动入口
if __name__ == '__main__':
    asyncio.run(main())
