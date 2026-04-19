import redis

class Redis:
    def __init__(self,config):
        self.config = config
        self.conn = redis.Redis(host=self.config['host'],port=self.config['port'],db=self.config['db'],password=self.config['password'],decode_responses=True)

    def getconn(self):
        return self.conn

    def close(self):
        self.conn.close()

if __name__ == '__main__':

    # 开发环境：后台: 11  web: 12   测试环境： 后台：5，web 6
    cfg_dev = {
        'host': 'r-wz9vnszvavqxpvchj2pd.redis.rds.aliyuncs.com',
        'port': 6379,
        'db': 6,
        "password": "brt9qdc*ckh8qda_GKT",
    }

    redis = Redis(cfg_dev)
    conn = redis.getconn()
    keys = conn.execute_command("keys *")
    for key in keys:
        type = conn.type(key)
        print(f"{key}: {type}")