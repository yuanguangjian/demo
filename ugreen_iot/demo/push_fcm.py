"""Firebase Cloud Messaging 推送 demo（原 `ipc项目/push.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

from pathlib import Path
from typing import Optional

from common.logger import get_logger

_logger = get_logger(__name__)


def send_notification(
    title: str,
    body: str,
    registration_token: str,
    *,
    credentials_file: str = "google.json",
) -> Optional[str]:
    """发送一条 FCM 通知。`credentials_file` 相对 demo/ 根目录。"""
    import firebase_admin
    from firebase_admin import credentials, messaging

    cred_path = Path(credentials_file)
    if not cred_path.is_absolute():
        cred_path = Path(__file__).resolve().parent.parent.parent / credentials_file
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(str(cred_path)))

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=registration_token,
    )
    response = messaging.send(message)
    _logger.info("FCM 发送成功：%s", response)
    return response


if __name__ == "__main__":
    token = (
        "eyNrsShOTWK6XvgqtR6jat:APA91bGY4JhYjJYNQlongEqPIrUE5jzS5b1B_JWPn9RgZxEkjVga5vUvzeQxYmupB9J1qNB9SleCyIuKJxhSLLw-86niN6idqL8yehrJu7GDEcMWZ3UsmSc"
    )
    send_notification("测试通知", "这是来自 Python 的推送消息", token)
