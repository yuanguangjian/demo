"""MQTT 批量连接/压测：合并历史 4 份脚本。

支持 backend：
- `"gmqtt"`：asyncio + gmqtt，可分批启动、限制并发数（原 `EMQX.py` / `xxxx.py`）。
- `"paho"`：多线程 + paho.mqtt（原 `EMQX_x.py` / `EMQX_xxx.py`）。

用户来源：
- `users=[{"user_id": "...", "password": "..."}, ...]` 直接传入，
- 或 `load_users_from_csv(path)` / `load_users_from_json(path, password=...)` 从文件读取。
"""
from __future__ import annotations

import csv
import json
import logging
import random
import threading
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from ..logger import get_logger

_logger = get_logger(__name__)


@dataclass
class MqttUser:
    user_id: str
    password: str


def load_users_from_csv(path: str) -> List[MqttUser]:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [MqttUser(row["user_id"], row["password"]) for row in reader]


def load_users_from_json(path: str, *, password: str) -> List[MqttUser]:
    """兼容原 `EMQX_x.py`：JSON 里只有用户名列表，密码统一给。"""
    with open(path, "r", encoding="utf-8") as f:
        usernames = json.load(f)
    return [MqttUser(str(u), password) for u in usernames]


# ---------- gmqtt (asyncio) ----------


async def _connect_gmqtt(
    user: MqttUser,
    *,
    host: str,
    port: int,
    topic: str,
    message: str,
    keepalive: int,
    hold_seconds: int,
    connect_timeout: float,
) -> None:
    import asyncio

    from gmqtt import Client as MQTTClient

    client_id = f"client_{user.user_id}_{random.randint(1000, 9999)}"
    client = MQTTClient(client_id)
    client.set_auth_credentials(user.user_id, user.password)
    client.on_connect = lambda *_: client.publish(topic, message)
    client.on_disconnect = lambda c, packet, exc=None: _logger.warning("断开: %s 原因: %s", c._client_id, exc)

    try:
        await asyncio.wait_for(client.connect(host, port, keepalive=keepalive), timeout=connect_timeout)
        await asyncio.sleep(hold_seconds)
    except asyncio.TimeoutError:
        _logger.warning("%s 连接超时", client_id)
    except Exception as exc:
        _logger.warning("%s 异常: %s", client_id, exc)


async def run_gmqtt(
    users: Sequence[MqttUser],
    *,
    host: str,
    port: int = 1883,
    topic: str = "/hello",
    message: str = "HELLO",
    keepalive: int = 60,
    hold_seconds: int = 1200,
    batch_size: int = 10,
    max_concurrency: int = 1000,
    batch_interval: float = 1.0,
    connect_timeout: float = 50.0,
) -> None:
    import asyncio

    logging.getLogger("gmqtt").setLevel(logging.WARNING)
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _one(u: MqttUser) -> None:
        async with semaphore:
            await _connect_gmqtt(
                u,
                host=host,
                port=port,
                topic=topic,
                message=message,
                keepalive=keepalive,
                hold_seconds=hold_seconds,
                connect_timeout=connect_timeout,
            )

    all_tasks = []
    total = len(users)
    _logger.info("总用户数: %s", total)
    for i in range(0, total, batch_size):
        batch = users[i : i + batch_size]
        all_tasks.extend(asyncio.create_task(_one(u)) for u in batch)
        _logger.info("启动第 %s 批 (%s 个)", i // batch_size + 1, len(batch))
        await asyncio.sleep(batch_interval)
    await asyncio.gather(*all_tasks)


# ---------- paho (threads) ----------


def _connect_paho(
    user: MqttUser,
    *,
    host: str,
    port: int,
    topic: str,
    message: str,
    keepalive: int,
    hold_seconds: int,
    publish_on_connect: bool,
) -> None:
    import paho.mqtt.client as mqtt

    client_id = f"client_{user.user_id}"

    def on_connect(c, userdata, flags, rc):  # type: ignore[no-untyped-def]
        _logger.info("[%s] 连接结果: %s", user.user_id, mqtt.connack_string(rc))
        if rc == 0 and publish_on_connect and message:
            c.publish(topic, message, qos=1)

    client = mqtt.Client(client_id=client_id, userdata={"user_id": user.user_id})
    client.username_pw_set(user.user_id, user.password)
    client.on_connect = on_connect
    client.connect(host, port, keepalive=keepalive)
    client.loop_start()
    try:
        time.sleep(hold_seconds)
    finally:
        client.loop_stop()
        client.disconnect()


def run_paho(
    users: Iterable[MqttUser],
    *,
    host: str,
    port: int = 1883,
    topic: str = "/hello",
    message: str = "",
    keepalive: int = 60,
    hold_seconds: int = 1,
    publish_on_connect: bool = False,
    rate_per_sec: float = 100.0,
) -> None:
    """`rate_per_sec`：控制启动速率，每连一个 sleep 1/rate。"""
    threads: List[threading.Thread] = []
    sleep_between = 1.0 / rate_per_sec if rate_per_sec > 0 else 0

    for user in users:
        t = threading.Thread(
            target=_connect_paho,
            args=(user,),
            kwargs=dict(
                host=host,
                port=port,
                topic=topic,
                message=message,
                keepalive=keepalive,
                hold_seconds=hold_seconds,
                publish_on_connect=publish_on_connect,
            ),
        )
        t.start()
        threads.append(t)
        if sleep_between:
            time.sleep(sleep_between)

    for t in threads:
        t.join()
    _logger.info("paho backend: 全部线程完成")


# ---------- EMQX Dashboard HTTP API ----------


def list_clients(dashboard_host: str, app_id: str, app_secret: str, *, timeout: float = 10.0):
    """调用 EMQX Dashboard REST `GET /api/v5/clients`（原 `emxxx.py`）。"""
    import base64

    import requests

    auth = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"basic {auth}",
    }
    return requests.get(f"{dashboard_host}/api/v5/clients", headers=headers, timeout=timeout).json()


# ---------- 用户 CSV 生成 ----------


def generate_user_csv(
    path: str,
    *,
    count: int = 10000,
    start_id: int = 2000,
    password: str = "Aa123456",
    is_superuser: str = "FALSE",
) -> None:
    """生成批量 MQTT 用户 CSV（原 `xx_csv.py`）。"""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "password", "is_superuser"])
        writer.writeheader()
        for i in range(count):
            writer.writerow(
                {
                    "user_id": f"{i + start_id:06d}",
                    "password": password,
                    "is_superuser": is_superuser,
                }
            )
    _logger.info("已生成 %s", path)
