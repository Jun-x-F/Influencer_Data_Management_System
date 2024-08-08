"""
@ProjectName: python
@FileName：logger.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/11 上午11:35
"""
import functools
import inspect
import os
import sys
import traceback
from typing import Dict

import pymysql
from loguru import logger

from log.log_template import Log


class LoguruLogger:
    def __init__(self,
                 log_level="INFO",
                 console=False,
                 isOpenError=False):
        """
        :param log_level:日志等级
        :param console: 是否打印日志
        :param isOpenError: 是否返回异常
        """
        # 数据库配置文件
        self.config = {
            'host': '120.79.205.19',
            'user': 'user1',
            'password': 'MisAdmin123#.',
            'database': 'log_data'
        }

        # DATABASE_URL = f"mysql+pymysql://{self.config.get('user')}:{self.config.get('password')}@{self.config.get('host')}/{self.config.get('database')}"
        #
        # # 配置连接池
        # engine = create_engine(
        #     DATABASE_URL,
        #     pool_size=10,  # 连接池大小
        #     max_overflow=20,  # 最大溢出连接数
        #     pool_timeout=30,  # 获取连接超时时间
        #     pool_recycle=1800  # 连接回收时间
        # )
        #
        # # 创建表
        # Base.metadata.create_all(engine)
        # Session = sessionmaker(bind=engine)
        # self.session = Session()
        #
        # # 移除默认的日志记录器
        logger.remove()
        #
        self.isOpenError = isOpenError
        #
        # # 添加日志文件记录器
        # logger.add(
        #     self.db_handle,
        #     level="ERROR",  # 设置日志级别 优化日志文件输出格式
        #     enqueue=True,
        #     serialize=True  # 设置序列化
        # )

        # 添加控制台输出记录器
        if console:
            logger.add(
                sys.stdout,
                level=log_level.upper(),
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{file}:{line}</cyan> | <white>{message}</white>",
                # 优化控制台输出格式
                colorize=True  # 启用颜色
            )

    def _db_init(self):
        # 数据库表初始化
        self.conn = pymysql.connect(**self.config)
        with self.conn.cursor() as cursor:
            sql = """
                CREATE TABLE IF NOT EXISTS logs (
                    id bigint PRIMARY KEY auto_increment comment '自动生成的uuid',  
                    time TEXT comment '时间',
                    level TEXT comment '日志等级',
                    file TEXT comment '文件名',
                    line INTEGER comment '文件行数',
                    message TEXT comment '信息',
                    exception_type TEXT comment '报错原因', 
                    exception_value TEXT comment '报错信息',
                    exception_file TEXT comment '报错文件', 
                    exception_func TEXT comment '报错函数名', 
                    exception_line INTEGER comment '报错行数', 
                    exception_info TEXT comment '报错堆栈信息'
                );
            """
            cursor.execute(sql)
        return self.conn

    def _log_to_db(self, record: Dict) -> None:
        try:
            log_entry = Log(
                time=record.get('time'),
                level=record.get('level'),
                file=record.get('file'),
                line=record.get('line'),
                message=record.get('message'),
                exception_type=record.get('exception_type'),
                exception_value=record.get('exception_value'),
                exception_file=record.get('exception_file'),
                exception_func=record.get('exception_func'),
                exception_line=record.get('exception_line'),
                exception_info=record.get('exception_info')
            )
            self.session.add(log_entry)
            self.session.commit()
        except Exception as e:
            print(f"Failed to log to database: {e}")
            self.session.rollback()

    def db_handle(self, message):
        record = message.record
        exception_type = None
        exception_value = None
        exception_file = None
        exception_line = None
        exception_info = None
        exception_func = None
        exception_file_name = None
        exception_file_line = None
        if record.get('extra'):
            exception_type = record["extra"].get("exception_type", None)
            exception_value = record["extra"].get("exception_value", None)
            exception_file = record["extra"].get("exception_file", None)
            exception_line = record["extra"].get("exception_line", None)
            exception_info = record["extra"].get("exception_info", None)
            exception_func = record["extra"].get("exception_func", None)
            exception_file_name = record["extra"].get("errorFileName", None)
            exception_file_line = record["extra"].get("errorFileLine", None)

        file = exception_file if exception_file else exception_file_name
        line = exception_line if exception_line else exception_file_line
        if file is None:
            file = str(record['file'].path)
        if line is None:
            line = str(record['line'])

        _to_message = {
            "time": record['time'].strftime('%Y-%m-%d %H:%M:%S'),
            "level": record['level'].name,
            "file": os.path.basename(file) if file else None,
            "line": line,
            "message": record['message'],
            "exception_type": exception_type,
            "exception_value": exception_value,
            "exception_file": exception_file,
            "exception_func": exception_func,
            "exception_line": exception_line,
            "exception_info": exception_info,
        }

        self._log_to_db(_to_message)

    def debug(self, message):
        logger.opt(depth=1).debug(message)

    def info(self, message):
        logger.opt(depth=1).info(message)

    def warning(self, message):
        logger.opt(depth=1).warning(message)

    def error(self, message=None):
        # 获取调用此方法的文件名
        caller_frame = inspect.stack()[1]
        caller_file = caller_frame.filename
        caller_line = caller_frame.lineno
        caller_function = caller_frame.function
        self.log_exception(message, caller_file, caller_line, caller_function)

    def log_exception(self, errorNotice=None, errorFileName=None, errorFileLine=None, func_name=None):
        exception_file = None
        exception_line = None
        exception_type = None
        exception_func = None
        exception_value = None
        exception_info = None
        exc_type, exc_value, exc_traceback = sys.exc_info()

        if exc_traceback:
            tb = exc_traceback
            file_stack = None

            while tb is not None:
                if tb.tb_frame.f_code.co_name == func_name:
                    file_stack = tb
                    break
                tb = tb.tb_next

            if file_stack is None:
                file_stack = exc_traceback
            exception_file = file_stack.tb_frame.f_code.co_filename
            exception_line = file_stack.tb_lineno
            exception_func = file_stack.tb_frame.f_code.co_name
            exception_info = ''.join(traceback.format_tb(exc_traceback))
            exception_type = exc_type.__name__
            exception_value = str(sys.exc_info())
        message = {
            "exception_type": exception_type,
            "exception_value": exception_value,
            "exception_file": exception_file,
            "exception_line": exception_line,
            "exception_info": exception_info,
            "exception_func": exception_func,
            "errorFileName": errorFileName,
            "errorFileLine": errorFileLine
        }
        if errorNotice:
            logger.bind(**message).error(errorNotice)
        else:
            logger.bind(**message).error(
                f"{os.path.basename(exception_file)} {exception_func}:{exception_line} {exc_type.__name__}")

    def log_exceptions(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                self.log_exception(func_name=func.__name__)
                if self.isOpenError:
                    raise  # 重新抛出异常以确保在上层捕获

        return wrapper

    def log_exceptions_async(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:

                self.log_exception(func_name=func.__name__)
                if self.isOpenError:
                    raise  # 重新抛出异常以确保在上层捕获

        return wrapper

    def critical(self, message):
        logger.opt(depth=1).critical(message)

    def catch(self, *args, **kwargs):
        return logger.catch(*args, **kwargs)

    def get_exception_info(self):
        """
        @FunctionName：get_exception_info
        @Description：
        @Author：Libre
        @Return:
        @CreateDate: 2023/6/1
        """
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exception_info = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
            "报错具体": except_traceback.tb_frame,
        }
        return exception_info


log = LoguruLogger()


@log.log_exceptions
def test():
    raise TypeError


@log.log_exceptions_async
async def test_exception_logging():
    raise ValueError("这是一个测试异常")


# @log.log_exceptions_async
async def test_message_exception_logging():
    log.error("测试")


# 示例用法
if __name__ == "__main__":
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    # test()
    # asyncio.run(test_exception_logging())
    # asyncio.run(test_message_exception_logging())
#     # 运行异步任务
#     # asyncio.run(main())
#     log.critical("This is a critical message")
