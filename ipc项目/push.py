import firebase_admin
from firebase_admin import credentials, messaging

# 替换为你的服务账号 JSON 文件路径
cred = credentials.Certificate("google.json")
firebase_admin.initialize_app(cred)

# 替换为你的设备 FCM Token
registration_token = "eyNrsShOTWK6XvgqtR6jat:APA91bGY4JhYjJYNQlongEqPIrUE5jzS5b1B_JWPn9RgZxEkjVga5vUvzeQxYmupB9J1qNB9SleCyIuKJxhSLLw-86niN6idqL8yehrJu7GDEcMWZ3UsmSc"

# 构建消息
message = messaging.Message(
    notification=messaging.Notification(
        title="测试通知",
        body="这是来自 Python 的推送消息",
    ),
    token=registration_token,
)

# 发送消息
response = messaging.send(message)
print("成功发送消息，响应 ID:", response)


