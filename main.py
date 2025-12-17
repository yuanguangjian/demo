from datetime import datetime, timedelta
import requests

# 给定的日期
time_str = '2024-12-22'
parsed_time = datetime.strptime(time_str, '%Y-%m-%d')

# 创建一个时间差对象，表示 14 天
time_difference = timedelta(days=14)

# 将 14 天添加到给定的日期
new_time = parsed_time + time_difference

# 输出结果
print(new_time.strftime('%Y-%m-%d'))  # 格式化输出为 'YYYY-MM-DD'

for i in range(50000):
    a = requests.get("https://dev3.ugreeniot.com/app/v1/product/model/ugreen_home?serialNo=6da5600dd430444683622e2b9d81ad9b",headers={'language':'zh'},data=None)
    print(a.text)
