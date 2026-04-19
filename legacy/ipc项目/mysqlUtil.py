import mysql.connector

config = {
    "dev": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_dev",
        "password": "AXwer!@#$!$@123",
        "database": "ugreen_dpt_dev",
        "port": 3306,
    },
    "test": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_test",
        "password": "AXwer!@#$!$@123",
        "database": "ugreen_dpt_test",
        "port": 3306,
    },
    "dvt": {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_dvt",
        "password": "VuX771t!iNniH9DB",
        "database": "ugreen_dpt_dvt",
        "port": 3306,
    }
}


class Mysql:
    def __init__(self, config):
        self.config = config
        self.conn = mysql.connector.connect(host=self.config['host'], user=self.config['user'],
                                            password=self.config['password'], database=self.config['database'],
                                            port=self.config['port'])
        self.cursor = self.conn.cursor()

    def select(self, sql):
        data = []
        self.cursor.execute(sql)
        columns = [desc[0] for desc in self.cursor.description]  # 获取字段名
        results = self.cursor.fetchall()
        for row in results:
            data.append(dict(zip(columns, row)))  # 将字段名与值组合成字典输出
        return data

    def insert(self, sql):
        try:
            self.conn.start_transaction()
            self.cursor.execute(sql)
            self.conn.commit()
            print("插入成功并已提交事务")
        except Exception as e:
            self.conn.rollback()
            print("插入失败，事务已回滚:", e)

    def close(self):
        self.cursor.close()
        self.conn.close()


def getData(env, database, sql):
    cfg = config[env]
    cfg["database"] = database
    mysql = Mysql(cfg)
    return mysql.select(sql)

def delete(env, database, sql):
    cfg = config[env]
    cfg["database"] = database
    mysql = Mysql(cfg)
    return mysql.insert(sql)

if __name__ == '__main__':
    dev_config = {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_dev",
        "password": "AXwer!@#$!$@123",
        "database": "ugreen_dpt_dev",
        "port": 3306
    }

    test_config = {
        "host": "rm-wz9h6s898dole0ubjoo.mysql.rds.aliyuncs.com",
        "user": "ugreen_test",
        "password": "AXwer!@#$!$@123",
        "database": "ugreen_dpt_test",
        "port": 3306
    }

    mysql = Mysql(test_config)

    sql = "SELECT *  from ipc_device_online_record limit 10;"
    data = mysql.select(sql)
    print(data)
    mysql.close()
