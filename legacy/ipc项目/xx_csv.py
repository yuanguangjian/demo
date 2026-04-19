import csv

# 配置参数
start_id = 2000
count = 10000  # 要生成多少个用户
password = "Aa123456"
is_superuser = "FALSE"

# 构造设备列表
devices = []
for i in range(count):
    user_id = f"{i + start_id:06d}"  # 补零到6位，如 001155
    devices.append({
        "user_id": user_id,
        "password": password,
        "is_superuser": is_superuser
    })

# 写入 CSV 文件
with open("devices_status.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["user_id", "password", "is_superuser"])
    writer.writeheader()
    writer.writerows(devices)

print("CSV 文件已生成：devices_status.csv")
