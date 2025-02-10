"""
@ProjectName: Influencer_Data_Management_System
@FileName: encrypt.py
@Author: Libre
@Time: 2024/3/21
@Description: 加密模块，提供AES加密功能
"""
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def encrypt_public_key(key: str) -> str:
    """
    使用AES-CBC模式加密字符串
    
    Args:
        key: 需要加密的字符串
        
    Returns:
        str: Base64编码的加密结果
        
    Raises:
        Exception: 加密过程中的异常
    """
    try:
        # 固定的密钥和IV（在生产环境中应该安全存储）
        secret_key = b'0123456789abcdef0123456789abcdef'  # 32位密钥
        iv = b'0123456789abcdef'  # 16位初始向量
        
        # 创建AES-CBC加密器
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        
        # 对数据进行填充并加密
        padded_data = pad(key.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        
        # 将加密结果转换为Base64编码
        return base64.b64encode(encrypted_data).decode('utf-8')
        
    except Exception as e:
        print(f'加密失败: {str(e)}')
        return '' 
    