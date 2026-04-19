"""查询 IPC 绑定 + SN + 密钥信息（原 `utils/ipc_data.py`）。

与原脚本相比：
- 用 `common.db.mysql.MySQLClient` 统一连接管理。
- 所有 SQL 改为参数化（`%s`），消除原 f-string 拼接的注入风险。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from common.db.mysql import MySQLClient
from common.logger import get_logger

_logger = get_logger(__name__)


def main(env: str = "test") -> None:
    bind_db = MySQLClient(env=env, database="ugreen_dpt_test")
    meta_db = MySQLClient(env=env, database="ugreen_dpt_metadata_test")

    bind_sql = (
        "SELECT product_serial_no, device_unique_code "
        "FROM user_bind_info "
        "WHERE product_serial_no IN (%s, %s) "
        "ORDER BY product_serial_no"
    )
    binds = bind_db.select(bind_sql, ("Camera001", "010001"))

    for row in binds:
        sn = row["device_unique_code"]
        product_model = row["product_serial_no"]
        _logger.info("%s@@%s", product_model, sn)

        sn_rows = meta_db.select(
            "SELECT sn,product_model,region,mac,first_time,`status`,product_no,sku,scan_in_time "
            "FROM ugreen_sn WHERE sn=%s AND product_model=%s",
            (sn, product_model),
        )
        for _ in sn_rows:
            secret_rows = meta_db.select(
                "SELECT sn,product_model,version,public_key "
                "FROM ugreen_sn_secret WHERE sn=%s AND product_model=%s",
                (sn, product_model),
            )
            for r in secret_rows:
                _logger.info("%s_%s_%s", product_model, sn, r["version"])


if __name__ == "__main__":
    main()
