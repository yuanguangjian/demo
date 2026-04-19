"""批量生成 MQTT 压测用户 CSV（原 `ipc项目/xx_csv.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import argparse

from common.logger import get_logger
from common.mqtt.stress import generate_user_csv

_logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 MQTT 压测用户 CSV")
    parser.add_argument("--output", default="devices_status.csv")
    parser.add_argument("--start-id", type=int, default=2000)
    parser.add_argument("--count", type=int, default=10000)
    parser.add_argument("--password", default="Aa123456")
    args = parser.parse_args()

    generate_user_csv(
        args.output,
        start_id=args.start_id,
        count=args.count,
        password=args.password,
    )
    _logger.info("已生成 %s", args.output)


if __name__ == "__main__":
    main()
