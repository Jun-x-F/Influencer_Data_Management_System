"""
@ProjectName: DataAnalysis
@FileName：proxy_template.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午1:41
"""
from log.logger import global_log

global_log.info("配置proxy文件成功...")

proxy_url = "brd.superproxy.io:22225"
proxy_user = "brd-customer-hl_152b8c40-zone-deone"
proxy_pass = "ep2dtcj1gf2b"

proxy = {
    'http': f'http://{proxy_user}:{proxy_pass}@{proxy_url}',
    'https': f'http://{proxy_user}:{proxy_pass}@{proxy_url}'
}
