"""绿联 App 用户账号：getSidInfo + RSA 分段加密 + 登录/注册/找回密码。

合并 `ipc项目/login.py` 与 `demo/用户登录注册相关接口.py`。
"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:  # 作为包导入时不需要
    pass

import base64
import json
from typing import Any, Dict, Optional, Tuple

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from common.config import env_base_url, load_json, save_json
from common.logger import get_logger

_logger = get_logger(__name__)

_MAX_ENCRYPT_BLOCK = 256


class UserAuth:
    """对自家 `/app/v1/user/*` 接口的客户端封装。"""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}

    # ---------- 加密 ----------

    def _get_sid_info(self) -> Optional[Tuple[str, str]]:
        url = f"{self.base_url}/app/v1/user/security/getSidInfo"
        resp = requests.post(url, headers=self.headers, timeout=10)
        if resp.status_code != 200:
            _logger.warning("getSidInfo 非 200: %s", resp.status_code)
            return None
        j = resp.json()
        if j.get("code") != 100000:
            _logger.warning("getSidInfo 业务失败: %s", j)
            return None
        return j["data"]["sid"], j["data"]["publicKey"]

    @staticmethod
    def _rsa_encrypt_segmented(data: Dict[str, Any], public_key_b64: str) -> str:
        key = RSA.import_key(base64.b64decode(public_key_b64))
        cipher = PKCS1_v1_5.new(key)
        raw = json.dumps(data).encode("utf-8")
        encrypted = bytearray()
        offset = 0
        while offset < len(raw):
            chunk = raw[offset : offset + _MAX_ENCRYPT_BLOCK]
            encrypted.extend(cipher.encrypt(chunk))
            offset += _MAX_ENCRYPT_BLOCK
        return base64.b64encode(encrypted).decode("utf-8")

    # ---------- 基础发送 ----------

    def _send(self, data: Any, path: str) -> Optional[requests.Response]:
        sid_info = self._get_sid_info()
        if not sid_info:
            return None
        sid, public_key = sid_info
        encoded = self._rsa_encrypt_segmented(data, public_key)
        if self.token:
            self.headers["Authorization"] = self.token
        return requests.post(
            f"{self.base_url}{path}",
            json={"sid": sid, "data": encoded},
            headers=self.headers,
            timeout=10,
        )

    def _send_and_parse(self, data: Any, path: str) -> Optional[Dict[str, Any]]:
        resp = self._send(data, path)
        if resp is None or resp.status_code != 200:
            return None
        return resp.json()

    def _apply_login_payload(self, j: Dict[str, Any]) -> Optional[str]:
        if j.get("code") != 100000:
            return None
        data = j["data"]
        self.token = data.get("token")
        self.refresh_token = data.get("refreshToken")
        return self.token

    # ---------- 注册 ----------

    def send_email_register_code(self, email: str) -> None:
        self._send({"email": email}, "/app/v1/user/register/sendEmailCode")

    def email_register(self, data: Dict[str, Any]) -> Optional[str]:
        j = self._send_and_parse(data, "/app/v1/user/register/emailRegister") or {}
        return self._apply_login_payload(j)

    def send_mobile_register_code(self, mobile: str) -> None:
        self._send({"mobile": mobile}, "/app/v1/user/register/sendMobileCode")

    def mobile_register(self, data: Dict[str, Any]) -> Optional[str]:
        j = self._send_and_parse(data, "/app/v1/user/register/mobileRegister") or {}
        return self._apply_login_payload(j)

    # ---------- 登录 ----------

    def email_login(self, data: Dict[str, Any]) -> Optional[str]:
        j = self._send_and_parse(data, "/app/v1/user/login/emailPasswordLogin") or {}
        return self._apply_login_payload(j)

    def mobile_password_login(self, data: Dict[str, Any]) -> Optional[str]:
        j = self._send_and_parse(data, "/app/v1/user/login/mobilePasswordLogin") or {}
        return self._apply_login_payload(j)

    def mobile_code_login_send(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._send_and_parse(data, "/app/v1/user/login/loginSendMobileCode")

    def mobile_code_login(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._send_and_parse(data, "/app/v1/user/login/mobileCodeLogin")

    def email_code_login_send(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._send_and_parse(data, "/app/v1/user/login/emailCodeLoginSendMailCode")

    def email_code_login(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self._send_and_parse(data, "/app/v1/user/login/emailCodeLogin")

    # ---------- 找回密码 ----------

    def send_mobile_reset_code(self, mobile: str) -> None:
        self._send({"mobile": mobile}, "/app/v1/user/safe/findPwdSendMobileCode")

    def reset_password_by_mobile(self, data: Dict[str, Any]) -> None:
        self._send(data, "/app/v1/user/safe/mobileFindPassword")

    def send_email_reset_code(self, email: str) -> None:
        self._send({"email": email}, "/app/v1/user/safe/findPwdSendMailCode")

    def reset_password_by_email(self, data: Dict[str, Any]) -> None:
        self._send(data, "/app/v1/user/safe/mailFindPassword")

    # ---------- 其它 ----------

    def get_user_info(self) -> Optional[requests.Response]:
        return self._send("hello", "/app/v1/user/getUserInfo")


# ---------- 给 http_client.on_unauthorized 钩子用 ----------


def build_relogin_hook(env: str):
    """返回一个 `hook(headers)`：401 时读取 `login.json[env]`，登录后改写 Authorization。"""
    from common.http_client import ReloginHook

    def _hook(headers: Dict[str, str]) -> None:
        account = load_json("login.json").get(env)
        if not account:
            _logger.warning("login.json 缺少 env=%s 的账号配置，无法 relogin", env)
            return
        user = UserAuth(env_base_url(env))
        if env == "ces":
            token = user.email_login(account)
        else:
            token = user.mobile_password_login(account)
        if token:
            headers["authorization"] = token

    _hook.__annotations__ = {"headers": Dict[str, str]}
    return _hook  # type: ignore[return-value]


# ---------- 本地 account.json 辅助 ----------


def get_account(key: str, file: str = "account.json") -> Optional[Dict[str, Any]]:
    return load_json(file).get(str(key))


def save_account(key: str, value: Dict[str, Any], file: str = "account.json") -> None:
    data = load_json(file)
    load_json.cache_clear()
    data[str(key)] = value
    save_json(file, data)


if __name__ == "__main__":
    base_url = "https://ces.ugreeniot.com/"
    user = UserAuth(base_url)
    user.email_login({"email": "1007503475@qq.com", "password": "Aa123456", "destroyFlag": 0})
