import mysql.connector
import fileUtil


class DB:

    def __init__(self, env, database):
        self.env = env
        self.config = fileUtil.openFile("mysql.json")[env]
        self.conn = mysql.connector.connect(host=self.config['host'], user=self.config['user'],
                                            password=self.config['password'], database=database,
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
            print("插入失败，事务已回滚:", e)

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    database = "ugreen_dpt_user_dev"
    db = DB("dev", database)
    data = db.select("select * from user limit 10")
    print(data)
