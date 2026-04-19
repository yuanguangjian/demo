import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email():
    # 邮件信息
    sender_email = "noreply_iot2@ugreen.com"  # 发件人邮箱
    receiver_email = "1007503475@qq.com"  # 收件人邮箱
    subject = "测试邮件"  # 邮件主题
    body = "<h1>这是一封测试邮件</h1>"  # 邮件内容（HTML格式）

    # 邮件服务器配置
    smtp_server = "smtp.exmail.qq.com"
    smtp_port = 465  # 或 587（如果使用 STARTTLS）
    password = "M9fZbDnAbn9DzD4F"  # 授权码

    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # 使用 HTML 格式的邮件内容

    try:
        # 连接到SMTP服务器
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # 使用 SSL 连接
        server.login(sender_email, password)  # 登录邮件服务器
        server.sendmail(sender_email, receiver_email, msg.as_string())  # 发送邮件
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")
    finally:
        server.quit()  # 退出连接


if __name__ == "__main__":
    send_email()
