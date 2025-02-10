"""
@ProjectName: Influencer_Data_Management_System
@FileName: request_config.py
@Author: Libre
@Time: 2024/3/21
@Description: 请求配置模块，提供请求头设置功能
"""
import time
from enum import Enum
from typing import Dict, Any, Optional

import requests

from spider.config.encrypt import encrypt_public_key


class TaskStatus(Enum):
    """任务状态枚举类"""
    PENDING = 0     # 待执行
    RUNNING = 1     # 正在执行
    COMPLETED = 2   # 完成任务
    FAILED = -1     # 任务执行失败/重复提交任务

class RequestConfig:
    """请求配置类，用于处理请求头和请求配置"""
    
    # 基础URL配置
    BASE_URL = "http://120.79.205.19:39090"
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """
        获取请求头信息
        
        Returns:
            Dict[str, str]: 包含必要认证信息的请求头字典
        """
        # 设置用户ID
        user_id = "spider_system"
        # 获取加密后的public_key
        public_key = encrypt_public_key(user_id)
        # 获取当前时间戳
        req_time = str(int(time.time())* 1000)
        
        headers = {
            "X-User-Id": user_id,
            "X-Public-Key": public_key,
            "X-Request-Time": req_time,
        }
        return headers

    @staticmethod
    def make_request(method: str, url: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求的通用方法
        
        Args:
            method: 请求方法（GET, POST, PUT, DELETE等）
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            requests.Response: 请求响应对象
            
        Raises:
            requests.RequestException: 请求过程中的异常
        """
        try:
            # 获取默认请求头
            headers = RequestConfig.get_headers()
            # print(headers)
            # 如果kwargs中有headers，则更新默认headers
            if 'headers' in kwargs:
                headers.update(kwargs.pop('headers'))
            
            # 发送请求
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            # 记录错误信息
            error_msg = f"请求失败: {str(e)}"
            raise requests.RequestException(error_msg)

    @classmethod
    def get_influencer_tasks(cls, task_type:str) -> Dict[str, Any]:
        """
        获取红人任务列表
        
        Returns:
            Dict[str, Any]: 红人任务数据
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
        """
        try:
            url = f"{cls.BASE_URL}/redisApi/tasks/{task_type}"
            response = cls.make_request('GET', url)
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"获取红人任务失败: {str(e)}")

    @classmethod
    def update_task_status(cls, task_id: str, status: TaskStatus, description: Optional[str] = None) -> Dict[str, Any]:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 任务状态（TaskStatus枚举类型）
            description: 可选的状态描述
            
        Returns:
            Dict[str, Any]: 更新结果
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
            ValueError: 参数验证失败时抛出异常
        """
        try:
            # 构建请求URL
            url = f"{cls.BASE_URL}/redisApi/tasks/{task_id}/status"
            
            # 构建查询参数
            params = {
                "status": status.value
            }
            
            # 如果提供了描述信息，添加到查询参数中
            if description is not None:
                params["description"] = description
                
            # 发送POST请求
            response = cls.make_request('POST', url, params=params)
            return response.json()
            
        except requests.RequestException as e:
            raise requests.RequestException(f"更新任务状态失败: {str(e)}")
        
if __name__ == '__main__':
    tasks = RequestConfig.get_influencer_tasks()
    # 处理返回的数据
    print(tasks)
    tasks = RequestConfig.update_task_status('6d50db2f18579dc0c0f4ee5738359b38', TaskStatus.COMPLETED)
    print(tasks)