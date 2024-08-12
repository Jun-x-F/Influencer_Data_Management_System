"""
@ProjectName: DataAnalysis
@FileName：test.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/18 上午11:36
"""
import asyncio

from log.logger import LoguruLogger

log = LoguruLogger()


@log.log_exceptions_async
async def test_exception_logging():
    raise ValueError("这是一个测试异常")


# @log.log_exceptions_async
async def test_message_exception_logging():
    try:
        await test_message_b()
    except Exception:
        log.error("这是一条测试的代码")



async def test_message_b():
    raise ValueError("异常数据")


# 示例用法
if __name__ == "__main__":
    #     log.debug("This is a debug message")
    #     log.info("This is an info message")
    #     log.warning("This is a warning message")
    # test()
    # asyncio.run(test_exception_logging())
    asyncio.run(test_message_exception_logging())
