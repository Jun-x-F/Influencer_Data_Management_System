"""
@ProjectName: DataAnalysis
@FileName：log_template.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/25 上午10:41
"""
import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='自动生成的UUID')
    time = Column(DateTime, default=datetime.datetime.utcnow, comment='时间')
    level = Column(String(50), comment='日志等级')
    file = Column(String(255), comment='文件名')
    line = Column(Integer, comment='文件行数')
    message = Column(Text, comment='信息')
    exception_type = Column(String(255), comment='报错原因')
    exception_value = Column(Text, comment='报错信息')
    exception_file = Column(String(255), comment='报错文件')
    exception_func = Column(String(255), comment='报错函数名')
    exception_line = Column(Integer, comment='报错行数')
    exception_info = Column(Text, comment='报错堆栈信息')


def init_db(connection_string):
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
