"""SMTP 发送邮件 demo（原 `my_email.py`）。"""
from __future__ import annotations

try:
    import _bootstrap  # noqa: F401
except ImportError:
    pass

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from common.logger import get_logger

_logger = get_logger(__name__)


SMTP_SERVER = "smtp.exmail.qq.com"
SMTP_PORT = 465
SMTP_USER = "noreply_iot2@ugreen.com"
SMTP_PASSWORD = "M9fZbDnAbn9DzD4F"


def send_html_mail(
    receiver: str,
    subject: str,
    html_body: str,
    *,
    sender: str = SMTP_USER,
    password: str = SMTP_PASSWORD,
    smtp_server: str = SMTP_SERVER,
    smtp_port: int = SMTP_PORT,
) -> bool:
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        _logger.info("邮件发送成功 -> %s", receiver)
        return True
    except Exception as e:
        _logger.error("邮件发送失败: %s", e)
        return False
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass


if __name__ == "__main__":
    send_html_mail("1007503475@qq.com", "测试邮件", "<h1>这是一封测试邮件</h1>")
