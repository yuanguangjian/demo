import requests
import login
import ipc_分享 as ipc1

config = {
    "dev": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_dev",
        "password": "AXwer!@#$!$@123",
        "database": "ugreen_dpt_dev",
        "port": 3306,
        "url": "https://dev3.ugreeniot.com"
    },
    "test": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_test",
        "password": "AXwer!@#$!$@123",
        "database": "ugreen_dpt_test",
        "port": 3306,
        "url": "https://test2.ugreeniot.com"
    }
}


def getUserInfo(phone, env):
    cfg = config[env]
    url = cfg["url"]
    login.login(url)



if __name__ == '__main__':
    mysql = Mysql(test_config)

    sql = "SELECT *  from ipc_device_online_record limit 10;"
    data = mysql.select(sql)
    print(data)
    mysql.close()
