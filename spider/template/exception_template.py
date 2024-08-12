"""
@ProjectName: DataAnalysis
@FileName：exception_template.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 下午3:16
"""


class RetryableError(Exception):
    """自定义重试异常类"""

    def __init__(self, message="A retryable error occurred", retry_count=0):
        super().__init__(message)
        self.retry_count = retry_count

