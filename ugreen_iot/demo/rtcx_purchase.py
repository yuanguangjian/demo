"""相速 RTCX 云存储购买/查询 demo。

原 `ipc项目/rtcx.py` 的 `unbind` / `getSnInfo` 函数由于**错误缩进**脱离了 `Rtcx` 类。
实际上这些方法已经在 `ugreen_iot.rtcx.Rtcx` 里（合并版）。本 demo 直接调用业务类。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from ugreen_iot.rtcx import Rtcx


if __name__ == "__main__":
    # 按手机号给账号下所有设备开通年包
    rtcx = Rtcx("dvt")
    phone = "13662558350"
    rtcx.buy_by_phone(phone)
    # 查询某 SN 的绑定/账号信息
    # rtcx.get_sn_info("I50000U59M100014")
