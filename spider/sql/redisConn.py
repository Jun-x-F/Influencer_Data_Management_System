import json
import pickle

import redis

from log.logger import LoguruLogger

logger = LoguruLogger()


class RedisClient:
    def __init__(self, host='localhost', port=6379, db=3):
        self.host = host
        self.port = port
        self.db = db
        self.connection = self.connect()

    def connect(self):
        try:
            connection = redis.Redis(host=self.host, port=self.port, db=self.db)
            # 测试连接
            connection.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}, db: {self.db}")
            return connection
        except redis.ConnectionError as e:
            print(e)
            logger.error()
            return None

    def set_value(self, key, value, expiration=None):
        try:
            self.connection.set(key, value, ex=expiration)
            logger.info(f"Set {key} = {value} with expiration = {expiration}")
        except Exception as e:
            logger.error()

    def get_value(self, key):
        try:
            value = self.connection.get(key)
            if value is not None:
                value = value.decode('utf-8')
            logger.info(f"Get {key} = {value}")
            return value
        except Exception as e:
            logger.error()
            return None

    def set_dataframe(self, key, df, expiration=None):
        try:
            # 序列化 DataFrame
            df_bytes = pickle.dumps(df)
            self.connection.set(key, df_bytes, ex=expiration)
            logger.info(f"Set DataFrame for key {key} with expiration = {expiration}")
        except Exception as e:
            logger.error()

    def get_dataframe(self, key):
        try:
            # 获取序列化的 DataFrame
            df_bytes = self.connection.get(key)
            if df_bytes is not None:
                df = pickle.loads(df_bytes)
                logger.info(f"Get DataFrame for key {key}")
                return df
            else:
                logger.warning(f"No DataFrame found for key {key}")
                return None
        except Exception as e:
            logger.error()
            return None


# 示例使用
if __name__ == "__main__":
    redis_client = RedisClient(host='172.16.11.245', port=6379, db=4)
    redis_client.set_value('test', '["测试"]')
    value = redis_client.get_value('test')
    print(json.loads(value))
    print(f"Value type: {type(json.loads(value))}")
