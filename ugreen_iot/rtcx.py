"""RTCX 云存储/解绑 业务客户端。

合并 `utils/ipc_rtcx.py` 与 `utils/ipc_rtcx_forceUnbind.py`：
- 去掉原文件中的**全局可变 `baseData`**（多次调用互相污染的坑），改为每次调用现构造。
- SQL 改为参数化（`%s`），消除 f-string 拼接注入面。
- 保留两种 `buy` 规格：默认按 `env+model` 查表；`buy(..., specifications=[...])` 可传自定义（原 forceUnbind 版）。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import datetime
import json
import uuid
from typing import Any, Dict, Iterable, List, Optional, Sequence

from common.crypto.aes import AESUtil
from common.db.mysql import MySQLClient
from common.logger import get_logger
from common.signing import hmac_rtcx

_logger = get_logger(__name__)

# 业务常量（保留原值）
_AES_KEY = "gh&*$P3124334343"
_OPEN_ID_APP_KEY = "JaLezS0jUtdcgOduHMgenKfUr"

_MODELS: Dict[str, str] = {
    "010001": "ID500 Pro",
    "010002": "OD600 Pro",
    "010004": "ID500 Plus",
    "010003": "D500",
}

_STATUS_MAP: Dict[int, str] = {
    0: "有效(使用中)",
    1: "无效(已过期)",
    2: "冻结(停用)",
}

_RTCX_URLS: Dict[str, str] = {
    "ces": "https://third-gateway.iotrtcus.com",
    "dvt": "https://third-gateway.iotrtc.cn",
    "dev": "https://third-gateway.iotrtc.cn",
    "test": "https://third-gateway.iotrtc.cn",
}

_DEFAULT_PRODUCTS: Dict[str, Dict[str, List[str]]] = {
    "ces": {
        "010001": ["event_7", "continuous_1_year"],
        "010002": ["event_7_lens2"],
        "010003": [],
        "010004": ["event_7", "continuous_1_year"],
    },
    "dvt": {
        "010001": ["event_30_day", "continuous_30_day"],
        "010002": ["continuous_7_lens2", "event_30_lens2"],
        "010003": [],
        "010004": ["event_30_day", "continuous_30_day"],
    },
}

_YEAR_PACK_PRODUCTS: List[str] = [
    "event_1_year",
    "continuous_1_year",
    "event_1_year_lens3",
    "continuous_1_year_lens3",
]


def _build_base_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """每次请求构造独立的 baseData；避免历史实现的全局可变字典污染。"""
    return {
        "id": str(uuid.uuid4()),
        "params": params,
        "request": {"apiVer": "1.0.0"},
        "version": "1.0",
    }


def _rtcx_post(path: str, params: Dict[str, Any], rtcx_url: str) -> str:
    """包一层：每次新 base + 经过签名网关 request。"""
    return _rtcx_util_request(path, _build_base_data(params), rtcx_url)


def _rtcx_util_request(path: str, body_dict: Dict[str, Any], url: str) -> str:
    """等价于旧 `rtcxUtil.request`：先获取 token 再 POST。"""
    import requests

    def _post(p: str, data: Dict[str, Any]) -> str:
        headers, body_bytes = hmac_rtcx.build_rtcx_headers("POST", p, data)
        resp = requests.post(url + p, headers=headers, data=body_bytes, timeout=15)
        return resp.text

    token_resp = json.loads(_post("/platform/cloud/token", _build_base_data({})))
    token = token_resp["data"]["accessToken"]
    body_dict = {**body_dict}
    body_dict["request"] = {**body_dict.get("request", {}), "cloudToken": token}
    return _post(path, body_dict)


class Rtcx:
    def __init__(self, env: str) -> None:
        self.env = env
        if env not in _RTCX_URLS:
            raise KeyError(f"rtcx 未定义环境 '{env}'")
        self.rtcx_url = _RTCX_URLS[env]

    # ---------- 云存储订单 ----------

    def freeze(self, iot_id: str, order_id: str) -> str:
        result = _rtcx_post(
            "/platform/vision/customer/cloudstorage/status/set",
            {"iotId": iot_id, "orderId": order_id, "status": 2},
            self.rtcx_url,
        )
        _logger.info("冻结 %s：%s", iot_id, result)
        return result

    def get_order_list(self, iot_id: str) -> None:
        result = _rtcx_post(
            "/platform/vision/customer/cloudstorage/order/query",
            {"iotId": iot_id},
            self.rtcx_url,
        )
        data = json.loads(result)
        _logger.info(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))
        if data.get("code") == 200:
            orders = (data.get("data") or {}).get("orderList") or []
            for order in orders:
                if order["status"] == 0:
                    self.freeze(iot_id, order["orderId"])

    def send_msg(self, open_id: str, data: Dict[str, Any]) -> str:
        result = _rtcx_post(
            "/platform/message/user/transfer",
            {"openId": open_id, "message": json.dumps(data)},
            self.rtcx_url,
        )
        _logger.info("发送消息：%s", result)
        return result

    def buy(
        self,
        iot_id: str,
        open_id: str,
        model: str = "",
        *,
        specifications: Optional[Sequence[str]] = None,
    ) -> None:
        """购买云存储套餐。

        - 默认按 `env + model` 查表取套餐（原 `ipc_rtcx.Rtcx.buy` 行为）。
        - 传入 `specifications=[...]` 时直接用；例如原 `ipc_rtcx_forceUnbind` 的年包列表。
        """
        if specifications is None:
            specifications = _DEFAULT_PRODUCTS.get(self.env, {}).get(model, [])
        for specification in specifications or []:
            result = _rtcx_post(
                "/platform/customer/cloudstorage/commodity/buy",
                {
                    "iotId": iot_id,
                    "userName": open_id,
                    "specification": specification,
                    "copies": "1",
                    "immediateUse": "true",
                },
                self.rtcx_url,
            )
            _logger.info("购买 %s：%s", specification, result)

    def buy_year_pack(self, iot_id: str, open_id: str) -> None:
        """等价于 `ipc_rtcx_forceUnbind.Rtcx.buy`：固定一年套餐。"""
        self.buy(iot_id, open_id, specifications=_YEAR_PACK_PRODUCTS)

    def products(self) -> None:
        result = _rtcx_post("/platform/customer/cloudstorage/commodity/query", {}, self.rtcx_url)
        _logger.info(json.dumps(json.loads(result), sort_keys=True, indent=4, ensure_ascii=False))

    def unbind(self, iot_id: str, open_id: str) -> str:
        result = _rtcx_post(
            "/platform/cloud/user/device/unbind",
            {"openId": open_id, "openIdAppKey": _OPEN_ID_APP_KEY, "iotId": iot_id},
            self.rtcx_url,
        )
        _logger.info("解绑 %s 用户 %s：%s", iot_id, open_id, result)
        return result

    def get_iot_buy(self, iot_id: str) -> None:
        result = _rtcx_post(
            "/platform/vision/customer/cloudstorage/order/query",
            {"iotId": iot_id},
            self.rtcx_url,
        )
        data = json.loads(result)
        if data.get("code") != 200:
            return
        orders = (data.get("data") or {}).get("orderList") or []
        for order in orders:
            record_type = order.get("recordType")
            status = order.get("status")
            specification = order.get("specification") or ""
            status_desc = _STATUS_MAP.get(status, f"未知状态({status})")
            if specification.startswith("event") or record_type == 2:
                log_type = "事件型套餐"
            elif specification.startswith("continuous") or record_type == 1:
                log_type = "云存储套餐"
            else:
                log_type = "未知套餐"
            if record_type == 1:
                end_time = order.get("endTime")
                end_str = (
                    datetime.datetime.fromtimestamp(end_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    if end_time
                    else "无到期时间"
                )
                _logger.info(
                    "[设备:%s] %s | 规格:%s | 状态:%s | 到期:%s | recordType:%s",
                    iot_id, log_type, specification, status_desc, end_str, record_type,
                )
            elif record_type == 2:
                _logger.info(
                    "[设备:%s] %s | 规格:%s | 状态:%s | recordType:%s",
                    iot_id, log_type, specification, status_desc, record_type,
                )

    # ---------- 账号查询（DB） ----------

    def _user_db(self) -> MySQLClient:
        return MySQLClient(self.env, f"ugreen_dpt_user_{self.env}")

    def _biz_db(self) -> MySQLClient:
        return MySQLClient(self.env, f"ugreen_dpt_{self.env}")

    def _meta_db(self) -> MySQLClient:
        return MySQLClient(self.env, f"ugreen_dpt_metadata_{self.env}")

    def _find_user_id_by_account(self, account: str) -> Optional[str]:
        phonex = AESUtil.encrypt(_AES_KEY, account)
        field = "user_mail" if self.env == "ces" else "user_mobile"
        sql = f"SELECT user_id FROM user WHERE status=1 AND {field}=%s AND destroy_status=1"
        with self._user_db() as db:
            rows = db.select(sql, (phonex,))
        return rows[0]["user_id"] if rows else None

    def _list_bindings(self, user_id: str) -> List[Dict[str, Any]]:
        sql = (
            "SELECT iot_id, open_id, sn, product_serial_no FROM ipc_bind_record "
            "WHERE status=1 AND bind_type=0 AND user_id=%s"
        )
        with self._biz_db() as db:
            return db.select(sql, (user_id,))

    def buy_by_phone(self, phone: str) -> None:
        user_id = self._find_user_id_by_account(phone)
        if not user_id:
            _logger.warning("用户不存在：%s", phone)
            return
        rows = self._list_bindings(user_id)
        for row in rows:
            _logger.info(
                "账号 %s 环境 %s userId=%s iotId=%s openId=%s 购买云存 + 事件",
                phone, self.env, user_id, row["iot_id"], row["open_id"],
            )
            self.buy(row["iot_id"], row["open_id"], row["product_serial_no"])

    def buy_by_sn(self, sn: str) -> None:
        sql = (
            "SELECT iot_id, open_id, sn, product_serial_no, user_id FROM ipc_bind_record "
            "WHERE status=1 AND bind_type=0 AND sn=%s"
        )
        with self._biz_db() as db:
            rows = db.select(sql, (sn,))
        if not rows:
            _logger.warning("sn 未绑定：%s", sn)
            return
        row = rows[0]
        _logger.info(
            "SN %s userId=%s iotId=%s openId=%s 购买云存 + 事件",
            sn, row["user_id"], row["iot_id"], row["open_id"],
        )
        self.buy(row["iot_id"], row["open_id"], row["product_serial_no"])

    def bind_info(self, phone: str) -> None:
        user_id = self._find_user_id_by_account(phone)
        if not user_id:
            _logger.warning("用户不存在：%s", phone)
            return
        rows = self._list_bindings(user_id)
        if not rows:
            _logger.info("账号 %s userId=%s 无绑定", phone, user_id)
            return
        for row in rows:
            self.get_iot_buy(row["iot_id"])
            _logger.info(
                "产品 %s sn=%s 账号 %s 环境 %s userId=%s iotId=%s openId=%s",
                row["product_serial_no"], row["sn"], phone, self.env,
                user_id, row["iot_id"], row["open_id"],
            )

    def all_bind_info(self, phone: str) -> None:
        user_id = self._find_user_id_by_account(phone)
        if not user_id:
            _logger.warning("用户不存在：%s", phone)
            return
        sql = """
            SELECT iot_id, open_id, sn, product_serial_no, bind_time, unbind_time, status
            FROM (
                SELECT iot_id, open_id, sn, product_serial_no, bind_time, unbind_time, status,
                       ROW_NUMBER() OVER (PARTITION BY iot_id ORDER BY bind_time DESC) AS rn
                FROM ipc_bind_record
                WHERE user_id = %s
            ) t WHERE rn = 1 ORDER BY status ASC
        """
        with self._biz_db() as db:
            rows = db.select(sql, (user_id,))
        for row in rows:
            self.get_iot_buy(row["iot_id"])
            bind_time = datetime.datetime.fromtimestamp(int(row["bind_time"] / 1000)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            unbind_time: Any = int(row["unbind_time"] / 1000)
            status = "绑定"
            if row["status"] == 0:
                status = "解绑"
                unbind_time = datetime.datetime.fromtimestamp(unbind_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            _logger.info(
                "产品 %s sn=%s 账号 %s userId=%s iotId=%s openId=%s 状态=%s 绑定=%s 解绑=%s",
                row["product_serial_no"], row["sn"], phone, user_id,
                row["iot_id"], row["open_id"], status, bind_time, unbind_time,
            )

    def get_sn_info(self, sn: str) -> None:
        with self._meta_db() as db:
            meta_rows = db.select(
                "SELECT sn.sn, sn.product_model, meta.product_key, meta.device_name, sn.status "
                "FROM ugreen_sn AS sn LEFT JOIN ugreen_sn_meta meta ON sn.sn = meta.sn "
                "WHERE sn.sn = %s",
                (sn,),
            )
        if not meta_rows:
            return
        meta = meta_rows[0]
        _logger.info(
            "基本信息: sn=%s 状态=%s productModel=%s productKey=%s deviceName=%s",
            sn, meta["status"], meta["product_model"], meta["product_key"], meta["device_name"],
        )
        with self._biz_db() as db:
            bindings = db.select(
                "SELECT user_id, open_id, iot_id, status, bind_type FROM ipc_bind_record "
                "WHERE sn=%s AND status=1",
                (sn,),
            )
        for user in bindings:
            bind_status = "绑定状态" if user["status"] == 1 else "解绑"
            bind_type = "被分享" if user["bind_type"] == 1 else "拥有者"
            self.get_iot_buy(user["iot_id"])
            _logger.info(
                "绑定：userId=%s openId=%s iotId=%s 状态=%s 类型=%s",
                user["user_id"], user["open_id"], user["iot_id"], bind_status, bind_type,
            )
            with self._user_db() as db:
                user_rows = db.select(
                    "SELECT user_mobile, user_mail FROM user WHERE user_id=%s",
                    (user["user_id"],),
                )
            if user_rows:
                u = user_rows[0]
                enc = u["user_mail"] if self.env == "ces" else u["user_mobile"]
                decrypted = AESUtil.decrypt(_AES_KEY, enc)
                _logger.info("账号: %s", decrypted)

    def force_unbind(self, sn: str) -> None:
        database = f"ugreen_dpt_{self.env}"
        with MySQLClient(self.env, database) as db:
            rows = db.select(
                "SELECT open_id, iot_id FROM ipc_bind_record "
                "WHERE sn=%s AND status=1 AND bind_type=0",
                (sn,),
            )
        if not rows:
            _logger.info("不存在绑定：%s", sn)
            return
        self.unbind(rows[0]["iot_id"], rows[0]["open_id"])

        clean_sqls: Sequence[tuple[str, tuple]] = (
            ("DELETE FROM user_bind_info WHERE device_unique_code=%s", (sn,)),
            ("DELETE FROM ipc_bind_record WHERE sn=%s", (sn,)),
            ("DELETE FROM ipc_share_qr_code WHERE device_unique_code=%s", (sn,)),
            ("DELETE FROM ipc_share_record WHERE device_unique_code=%s", (sn,)),
            ("DELETE FROM ipc_contact_label WHERE device_unique_code=%s", (sn,)),
            ("DELETE FROM ipc_device_event_record WHERE sn=%s", (sn,)),
        )
        with MySQLClient(self.env, database) as db:
            for sql, params in clean_sqls:
                _logger.info("%s %s", sql, params)
                db.execute(sql, params)

    def check_meta(self) -> None:
        for model, name in _MODELS.items():
            with self._meta_db() as db:
                total = db.select(
                    "SELECT COUNT(1) AS num FROM ugreen_meta WHERE product_model=%s", (model,)
                )
                un_use = db.select(
                    "SELECT COUNT(1) AS num FROM ugreen_meta WHERE status=0 AND product_model=%s",
                    (model,),
                )
            with self._biz_db() as db:
                bound = db.select(
                    "SELECT COUNT(1) AS num FROM user_bind_info WHERE product_serial_no=%s",
                    (model,),
                )
            _logger.info(
                "环境 %s 产品 %s(%s) 绑定=%s 三元组总量=%s 未使用=%s",
                self.env, model, name, bound[0]["num"], total[0]["num"], un_use[0]["num"],
            )


# ---------- 控制台登录辅助（原 ipc_rtcx_login） ----------


_CONSOLE_URLS: Dict[str, str] = {
    "dvt": "https://cloudapi.iotrtc.cn/oam/ep/list?pageNo=1&pageSize=10&total=0",
    "ces": "https://os-console.iotrtc.cn/oam/ep/list?pageNo=1&pageSize=10&total=0&",
}

_CONSOLE_DEFAULT_TK = (
    "tk=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJhdWQiOlsiMzI4IiwiMCIsIjcwZDY5ZGYyZTkwMDRkZThhNDUwYTA0YzkxYjhmZTRmIl0sImFjb2RlIjoiY2QwMDY5MmMzYmZlNTkyNjdkNWVjZmFjNTMxMDI4NmMiLCJleHAiOjE3NjM5OTI3NjJ9"
    ".ADawRKAL9qOzYHlwCrcj0t_NhFdonQSs0ZHZtIqqt_w"
)


class RtcxConsole:
    """取自 `utils/ipc_rtcx_login.py`：相速 OAM 控制台设备在线查询。"""

    def __init__(self, env: str, *, tk: str = _CONSOLE_DEFAULT_TK) -> None:
        self.env = env
        self.url = _CONSOLE_URLS.get(env, _CONSOLE_URLS["dvt"])
        self.tk = tk

    def get_info(self, device_name: str) -> None:
        import requests

        url = f"{self.url}&deviceName={device_name}" if device_name else self.url
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "x-tk": self.tk,
        }
        resp = requests.get(url, headers=headers, timeout=10)
        payload = resp.json()
        if payload.get("code") != 200:
            return
        items = (payload.get("data") or {}).get("items") or []
        if not items:
            return
        info = items[0]
        status = "在线" if info.get("onlineStatus") == 1 else "离线"
        _logger.info("相速平台: deviceName=%s status=%s", info["deviceName"], status)


if __name__ == "__main__":
    rtcx = Rtcx("ces")
    # rtcx.check_meta()
    # rtcx.bind_info("ningna@ugreen.com")
