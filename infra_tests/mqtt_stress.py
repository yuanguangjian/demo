"""MQTT 压测入口。

实际算法都在 `common.mqtt.stress` 里，这里只提供一个 CLI 风格的演示入口。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import argparse
import asyncio

from common.logger import get_logger
from common.mqtt.stress import load_users_from_csv, run_paho

_logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="MQTT 压测 demo")
    parser.add_argument("--host", default="192.168.75.132")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="/hello")
    parser.add_argument("--message", default="HELLO")
    parser.add_argument("--csv", default="devices_status1.csv", help="CSV 用户列表（含 user_id,password 列）")
    parser.add_argument("--keepalive", type=int, default=1200)
    parser.add_argument("--backend", choices=["paho", "gmqtt"], default="paho")
    args = parser.parse_args()

    users = load_users_from_csv(args.csv)
    _logger.info("加载用户 %s 个", len(users))

    if args.backend == "paho":
        run_paho(
            users=users,
            host=args.host,
            port=args.port,
            topic=args.topic,
            message=args.message,
            keepalive=args.keepalive,
        )
    else:
        from common.mqtt.stress import run_gmqtt

        asyncio.run(
            run_gmqtt(
                users=users,
                host=args.host,
                port=args.port,
                topic=args.topic,
                message=args.message,
                keepalive=args.keepalive,
            )
        )


if __name__ == "__main__":
    main()
