"""
@ProjectName: python
@FileName: mysql.py
@IDE: PyCharm
@Author: Libre
@Time: 2024/7/10 下午5:26
"""
from typing import Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, scoped_session


class Connect:
    def __init__(self, tag: int, database: str = None):
        self.engine: Optional[Engine] = None
        self.conn: Optional[Connection] = None
        self.session: Optional[scoped_session] = None
        if tag == 1:
            self.config = {
                'host': '120.79.205.19',
                'user': 'user1',
                'password': 'MisAdmin123#.',
                'database': database
            }
        elif tag == 2:
            self.config = {
                'host': '172.16.11.163',
                'user': 'user1',
                'password': 'user1',
                'database': database
            }
        else:
            raise ValueError("Invalid tag value. Must be 1 or 2.")

    def execute(self, sql: str) -> Any:
        if self.conn is None:
            raise ValueError("Connection is not established.")
        # Use SQLAlchemy's Connection object to execute SQL
        with self.conn.begin() as transaction:
            result = self.conn.execute(text(sql))
            return result.fetchall()

    def con_way(self) -> None:
        connection_string = \
            f"mysql+pymysql://{self.config['user']}:{self.config['password']}@{self.config['host']}/{self.config['database']}"
        self.engine = create_engine(connection_string,
                                    pool_size=10,  # 连接池大小
                                    max_overflow=20,  # 允许的最大溢出连接数
                                    pool_recycle=3600,  # 连接回收时间（秒）
                                    pool_timeout=30  # 连接超时时间（秒）
                                    )
        self.conn = self.engine.connect()

    def create_session(self) -> None:
        """建立session链接"""
        if self.engine is None:
            self.con_way()
        Session = sessionmaker(bind=self.engine)
        self.session = scoped_session(Session)

    def check_connection(self) -> bool:
        """判断连接是否存在"""
        try:
            self.conn.execute(text('select 1'))
            return True
        except OperationalError:
            return False

    def reconnect_session(self) -> None:
        """重新链接"""
        self.close()
        self.session.remove()
        self.create_session()

    def close(self) -> None:
        """关闭链接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.engine.dispose()
            self.engine = None
