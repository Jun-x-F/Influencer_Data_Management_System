"""
@ProjectName: DataAnalysis
@FileName：track_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 上午10:11
"""
import concurrent
import datetime
import json
import math
import os.path
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue
from typing import Optional

import pandas as pd
from playwright.sync_api import Page, sync_playwright, Response
from sqlalchemy.orm import scoped_session

from log.logger import global_log
from spider.config.config import headerLess, return_viewPort, user_agent, redis_conn
from spider.sql.data_inner_db import db
from spider.template.class_dict_template import FIFODict
from spider.template.proxy_template import proxy_user, proxy_pass, proxy_url
from spider.template.spider_db_template import logistics_information_sheet
from spider.track.track_global_info import global_json, global_track_info
from spider.translator.microsofttranslator import translate

isSavePath = False
order_queue = Queue()
cache_queue = Queue()
count_queue = FIFODict()
error_queue = Queue()
tf_dict = FIFODict()
# 定义一个全局事件，用于同步
shutdown_event = threading.Event()
recept_event = threading.Event()


class Task:
    def __init__(self, _page: Page, str_number: str):
        self.page: Page = _page
        self.human_wait_time = 6000
        self.response_data = None
        self.get_flag = False
        self.str_number = str_number
        global_log.info("装载爬虫获取的json")
        self.zh_cn = global_json

    def on_response(self, response: Response):
        if self.get_flag is True:
            return
        url = response.url
        if url in "https://t.17track.net/track/restapi":
            res_body = response.body()
            raw_res = json.loads(res_body)
            meta = raw_res.get("meta")
            code = meta.get("code")
            if code == 200:
                global_log.info(f"页面监听到指定request请求，进行解析...")
                self.response_data = raw_res.get("shipments")
                state = self.response_data[0].get("state")
                shipment = self.response_data[0].get("shipment")
                if state != 'Failure' and shipment is not None:
                    global_log.info(f"response数据获取成功，进行解析...")
                    global_log.info(self.response_data)
                    self.get_flag = True

    def get_proxy_info(self):
        try:
            # 访问一个返回地理位置的服务
            self.page.goto("https://ipinfo.io/json", wait_until="domcontentloaded")

            # 提取并打印地理位置信息
            geo_info = self.page.evaluate("() => JSON.parse(document.body.innerText)")
            global_log.info(
                f"IP: {geo_info['ip']} Country: {geo_info['country']} Region: {geo_info['region']} City: {geo_info['city']} Location: {geo_info['loc']}")
        except Exception:
            global_log.info("解析ip请求失败，继续执行任务")

    def click_info(self):
        if_login = False
        for _ in range(5):
            try:
                self.page.goto('https://www.17track.net/zh-cn', wait_until="domcontentloaded")
                if_login = True
                break
            except Exception:
                self.page.wait_for_timeout(self.human_wait_time)
        if if_login is False:
            global_log.info(
                f"目标https://www.track.net/zh-cn加载，累计等待{(self.human_wait_time * 5) / 1000}秒，重新回归队列中")
            order_queue.put(self.str_number)
            return if_login
        textarea = self.page.query_selector('//textarea[@id="auto-size-textarea"]')
        if textarea is None:
            global_log.info("检测不到输入框...重新加入队列中")
            order_queue.put(self.str_number)
            return False
        textarea.fill(self.str_number.replace(",", "\n"))
        self.page.wait_for_timeout(random.randint(0, self.human_wait_time))
        self.page.click(
            '//div[contains(@class, "batch_track_batch-track")]//*[contains(@title,"对输入的单号进行查询")]')
        return True

    def work(self):
        if_login = False
        # self.get_proxy_info()
        # res = self.click_info()
        # if res is False:
        #     return

        self.page.on("response", self.on_response)
        _url = f"https://t.17track.net/zh-cn#nums={self.str_number}"
        global_log.info(f"目标url为{_url}")
        for i in range(5):
            try:
                # https://t.17track.net/en#nums=
                self.page.goto(_url,
                               wait_until="domcontentloaded")
                if_login = True
                break
            except Exception as e:
                raise e
            finally:
                self.page.wait_for_timeout(self.human_wait_time * 2)
        if if_login is False:
            global_log.error(f"{_url}跳转失败，累计等待{(self.human_wait_time * 5) / 1000}秒，重新回归队列中")
            change_task_info(self.str_number, "retry")
            return

        # //a[text()="下一页"]
        close_ad = self.page.query_selector('//a[text()="下一页"]')
        if close_ad is not None:
            for _ in range(5):
                close_ad.click()
                if self.page.query_selector('//a[text()="完成"]'):
                    self.page.query_selector('//a[text()="完成"]').click()
                    break
                time.sleep(random.random())
            global_log.info("检测到指引，关闭指引完成")

        for _ in range(60 * 2):
            if self.get_flag is True:
                res, error_list = self.get_order_info()
                if res is False:
                    err_str = ",".join(error_list)
                    change_task_info(err_str, "retry")
                    global_log.error("解析数据出现异常，重新加入任务队列中")
                    raw_list = self.str_number.split(",")
                    result = list(set(raw_list) - set(error_list))
                    result_to_str = ",".join(result)
                    change_task_info(result_to_str, "finish")
                    break
                change_task_info(self.str_number, "finish")
                break

            reload = self.page.query_selector('//*[contains(text(), "网络访问错误，请进行重试")]')
            if reload is not None:
                global_log.info(f"页面识别到网络访问错误，进行刷新重试")
                self.page.reload(wait_until="domcontentloaded")
                self.page.wait_for_timeout(self.human_wait_time)

            # <h4 class="modal-title text-truncate">警告</h4>
            notice = self.page.query_selector('//h4[contains(text(), "警告")]')
            if notice is not None:
                global_log.info(f"页面识别到验证码，进行刷新重试")
                try:
                    self.page.reload(wait_until="domcontentloaded")
                    self.page.wait_for_timeout(self.human_wait_time)
                except Exception as e:
                    global_log.info("出现网络波动情况，需要检查网络")
                    raise e

            time.sleep(1)

    def contains_chinese(self, text):
        for char in text:
            if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf' or '\u20000' <= char <= '\u2a6df':
                return True
        return False

    def get_order_info(self) -> tuple[bool, Optional[list]]:
        _cur_error_list = []
        zh_cn_countries = self.zh_cn.get("country")
        for info in self.response_data:
            number = info.get("number")
            try:
                pre_status = None
                shipper_country_zn = None
                recipient_country_zn = None
                alias = None
                shipment_date = None,
                shipment_time = None,
                description = None,
                days_after_order = None,
                prior_status = info.get("prior_status")
                pre_status = info.get("pre_status")

                if prior_status == "NotFound" or prior_status is None:
                    order_cur_data = {
                        "number": number,
                        "alias": alias,
                        "prior_status": prior_status,
                        "prior_status_zh": "17track未查询到",
                        "shipper_country": shipper_country_zn,
                        "recipient_country": recipient_country_zn,
                        "shipment_date": shipment_date,
                        "shipment_time": shipment_time,
                        "description": description,
                        "days_after_order": days_after_order,
                    }

                    if isSavePath is True:
                        cache_queue.put(order_cur_data)
                    else:
                        cache_queue.put(logistics_information_sheet(**order_cur_data))
                    continue

                # 物流信息
                shipment = info.get("shipment")
                shipping_info = shipment.get("shipping_info")
                shipper_address = shipping_info.get("shipper_address")
                shipper_country = shipper_address.get("country")

                # _name
                if shipper_country is not None:
                    for zh_cn_country in zh_cn_countries:
                        if zh_cn_country.get("key").lower() == shipper_country.lower():
                            shipper_country_zn = zh_cn_country.get("_name")

                recipient_address = shipping_info.get("recipient_address")
                recipient_country = recipient_address.get("country")

                if recipient_country is not None:
                    for zh_cn_country in zh_cn_countries:
                        if zh_cn_country.get("key").lower() == recipient_country.lower():
                            recipient_country_zn = zh_cn_country.get("_name")
                latest_event = shipment.get("latest_event")
                time_raw = latest_event.get("time_raw")
                shipment_date = time_raw.get("date")
                shipment_time = shipment_date + " " + time_raw.get("time")
                description = latest_event.get("description")
                time_metrics = shipment.get("time_metrics")
                days_after_order = time_metrics.get("days_after_order")
                tracking = shipment.get("tracking")
                providers = tracking.get("providers")

                for _ in providers:
                    provider = _.get("provider")
                    if provider is not None:
                        alias = provider.get("alias")

                # 物流状态
                queryTranslate = [{
                    "text": prior_status
                }]

                translation_text = description
                # 判断是否有中文
                isChinese = self.contains_chinese(description)

                if isChinese is False:
                    # 追加 description
                    queryTranslate.append({
                        "text": description
                    })

                prior_status_zh_text = None

                for _info in global_track_info:
                    _key = _info.get("key")
                    if int(_key) == pre_status:
                        prior_status_zh_text = _info.get("_name")

                # 发送翻译请求
                translations = translate(json.dumps(queryTranslate))
                if len(translations) == 1 and prior_status_zh_text is None:
                    prior_status_zh_translations = translations[0].get("translations")
                    prior_status_zh_text = prior_status_zh_translations[0].get("text").encode('unicode_escape').decode(
                        'unicode_escape')
                elif len(translations) == 2 and prior_status_zh_text is None:
                    prior_status_zh_translations = translations[0].get("translations")
                    prior_status_zh_text = prior_status_zh_translations[0].get("text").encode('unicode_escape').decode(
                        'unicode_escape')
                    translation_text_translations = translations[1].get("translations")
                    translation_text = translation_text_translations[0].get("text").encode('unicode_escape').decode(
                        'unicode_escape')

                order_cur_data = {
                    "number": number,
                    "alias": alias,
                    "prior_status": prior_status,
                    "prior_status_zh": prior_status_zh_text,
                    "shipper_country": shipper_country_zn if shipper_country_zn is not None else shipper_country,
                    "recipient_country": recipient_country_zn if recipient_country_zn is not None else recipient_country,
                    "shipment_date": shipment_date,
                    "shipment_time": shipment_time,
                    "description": translation_text,
                    "days_after_order": days_after_order,
                }
                global_log.info(order_cur_data)
                if isSavePath is True:
                    cache_queue.put(order_cur_data)
                else:
                    cache_queue.put(logistics_information_sheet(**order_cur_data))
            except Exception as e:
                global_log.error(f"{number}解析数据出现异常，退出解析")
                global_log.error(info)
                _cur_error_list.append(number)
                continue
        if len(_cur_error_list) > 0:
            return False, _cur_error_list
        return True, None


def put_order_number_in_queue(retry_item=3, chunk_size=40) -> Optional[str]:
    """将数据不断推入order_queue中"""
    _cur_list = []
    for _order, info in count_queue.items():
        count = info.get("count")
        status = info.get("status")
        if status == "create":
            # 初始化
            _cur_list.append(_order)
        elif status == "done":
            continue
        elif status == "finish":
            continue
        elif count < retry_item and status == "retry":
            _cur_list.append(_order)
        else:
            error_queue.put(_order)
            info["status"] = "finish"
            info["thread_id"] = None
            count_queue[_order] = info

            redis_conn.set_value(_order, f"17track异常数据, 时间为{datetime.datetime.now()}", 20 * 24 * 3600)
            global_log.info(f"检测到{_order}出现获取异常次数不低于{retry_item}次，添加到Redis异常队列中，有效性20天")

    _cur_order_len = len(_cur_list)

    if _cur_order_len == 0:
        return "finish"

    _cur_order_item = math.ceil(_cur_order_len / chunk_size)
    start = 0
    for i in range(_cur_order_item):
        order_queue.put(",".join(_cur_list[start: (i + 1) * chunk_size]).strip(","))
        start = (i + 1) * chunk_size
    global_log.info(f"队列根据{chunk_size}条订单为一个任务，累计生成{order_queue.qsize()}个任务")


def same_to_count_queue(_order_list: list, isList=True):
    for _order in _order_list:
        # 将次数归为0
        if isList is True:
            count_queue[_order[0]] = {
                "count": 0,
                "status": "create"
            }
        else:
            count_queue[_order] = {
                "count": 0,
                "status": "create"
            }
    global_log.info(f"累计解析出来{len(count_queue)}条订单数据，开始添加到执行队列中")


def read_excel(file_path):
    """读取excel"""
    global_log.info(f"开始读取本地文件, 路径为{file_path}")
    df = pd.read_excel(file_path)
    _order_list = df.values.tolist()
    same_to_count_queue(_order_list)


def _cur(task):
    """执行任务"""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=headerLess,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            proxy={
                'server': f'https://{proxy_user}:{proxy_pass}@{proxy_url}',
                'username': proxy_user,
                'password': proxy_pass
            }
        )

        context = browser.new_context(
            viewport=return_viewPort(),
            user_agent=user_agent,
        )
        context.add_init_script(
            "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        )

        page = context.new_page()
        # stealth_sync(page)
        Task(page, task.upper()).work()


def commit_to_file_to_process(file_path: Path):
    instances = []
    error_instances = []
    while not error_queue.empty():
        error_instances.append(error_queue.get())

    while not cache_queue.empty():
        instances.append(cache_queue.get())

    if len(instances) != 0 or len(error_instances) != 0:

        new_df = pd.DataFrame(instances)
        if os.path.isfile(file_path):
            old_df = pd.read_excel(file_path)
            update_df = pd.concat([old_df, new_df]).drop_duplicates(subset=['number'],
                                                                    keep='last').reset_index(drop=True)
        else:
            update_df = new_df

        # 添加错误的 number 到 DataFrame 中，并标记 description 列为 "错误"
        if len(error_instances) > 0:
            for number in error_instances:
                if number in update_df['number'].values:
                    # 如果 number 存在，更新 description 列
                    update_df.loc[update_df['number'] == number, 'description'] = update_df.loc[update_df[
                                                                                                    'number'] == number, 'description'] + " - 错误"
                else:
                    # 如果 number 不存在，添加新行并标记 description 为 "错误"
                    error_df = pd.DataFrame({
                        'number': [number],
                        'alias': [None],  # 根据实际情况，可以留空或填充默认值
                        'prior_status': [None],
                        'shipper_country': [None],
                        'recipient_country': [None],
                        'shipment_date': [None],
                        'shipment_time': [None],
                        'description': ["错误"],
                        'days_after_order': [None]
                    })
                    update_df = pd.concat([update_df, error_df], ignore_index=True)

        # 保存更新后的 DataFrame 到 Excel 文件
        if len(instances) != 0:
            update_df.to_excel(file_path, index=False)

            global_log.info(f"数据已更新并保存到{file_path}，任务未结束前不要打开!")


def commit_to_file():
    desktop_path = Path.home() / "Desktop"
    file_path = desktop_path / f"{datetime.datetime.now().strftime('%Y-%m-%d')}_logistics_information.xlsx"
    global_log.info(f"文件存放路径为 {desktop_path}")
    while not shutdown_event.is_set():
        commit_to_file_to_process(file_path)
        time.sleep(5)
    commit_to_file_to_process(file_path)
    recept_event.set()


def commit_to_db_process(session: scoped_session):
    instances = []
    while not cache_queue.empty():
        instance = cache_queue.get()

        # 查询数据库中是否已有相同订单号和物流公司的记录
        existing_record = session.query(logistics_information_sheet).filter_by(
            number=instance.number).first()

        if existing_record:
            # 如果存在，则更新现有记录
            existing_record.prior_status = instance.prior_status
            existing_record.prior_status_zh = instance.prior_status_zh
            existing_record.shipper_country = instance.shipper_country
            existing_record.recipient_country = instance.recipient_country
            existing_record.shipment_time = instance.shipment_time
            existing_record.shipment_date = instance.shipment_date
            existing_record.description = instance.description
            existing_record.days_after_order = instance.days_after_order
            global_log.info(f"Updated existing record with number: {instance.number}, alias: {instance.alias}")
        else:
            # 如果不存在，则添加为新记录
            instances.append(instance)
            global_log.info(f"Added new record with number: {instance.number}, alias: {instance.alias}")

        cache_queue.task_done()

    if instances:
        session.add_all(instances)
        session.commit()
        global_log.info(f"Committed {len(instances)} new instances to the database.")
    else:
        session.commit()  # 提交更新的记录


def commit_to_db():
    if not db.check_connection():
        db.reconnect_session()
    session = db.session
    while not shutdown_event.is_set():
        commit_to_db_process(session)
        time.sleep(1)  # 每5秒检查一次队列是否有新的数据
    commit_to_db_process(session)
    recept_event.set()


def change_task_info(task: str, status: str):
    """修改状态，并将thread_id填写"""
    if "," not in task:
        info = count_queue.get(task)
        info["status"] = status
        if status == "retry":
            info["count"] = info["count"] + 1
        count_queue[task] = info
    else:
        task_list = task.split(",")
        for _ in task_list:
            info = count_queue.get(_)
            info["status"] = status
            if status == "retry":
                info["count"] = info["count"] + 1
            count_queue[_] = info


def thread_work():
    put_order_number_in_queue()
    while order_queue.empty() is False:
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {}
            for _ in range(min(5, order_queue.qsize())):
                # 批量获取任务
                task = order_queue.get()
                change_task_info(task, "done")
                future_to_url[executor.submit(_cur, task)] = task

            for future in as_completed(future_to_url):
                try:
                    # 超时3分钟
                    future.result(timeout=60 * 10)  # 确保获取任务的结果并处理异常
                except concurrent.futures.TimeoutError:
                    global_log.error(f"{task}任务超时，加入重试队列中")
                    change_task_info(task, "retry")
                except Exception as e:
                    raise
            put_order_number_in_queue()
    shutdown_event.set()
    global_log.info("任务执行完毕，等待队列同步数据中...")
    recept_event.wait(timeout=60 * 6)


def run(isRequest: bool = False, order_numbers: list = None):
    global isSavePath
    try:
        global_log.info("执行获取订单任务详情")
        if isRequest is False:
            isSavePath = True
            global_log.info("判断为人工手动操作")
            file_path = r"D:\wzhData\BaiduSyncdisk\project\python\DataAnalysis\物流-4-2024-08-14-1723627893.xlsx"
            # file_path = input("请输入文件路径(拖拽文件到此命令窗口，并回车即可): \n")
            read_excel(file_path)
            # 启动数据库提交线程
            commit_thread = threading.Thread(target=commit_to_file, daemon=True)
        else:
            global_log.info("判断为红人系统发出的请求操作")
            same_to_count_queue(order_numbers, isList=False)
            # 启动数据库提交线程
            commit_thread = threading.Thread(target=commit_to_db, daemon=True)
        commit_thread.start()
        thread_work()
        if isSavePath is False:
            if error_queue.qsize() > 0:
                raise ValueError(f"error_queue存在数据: {error_queue}")
        return True, "成功"
    except Exception as e:
        global_log.error()
        return False, "网络异常"


if __name__ == '__main__':
    run(True, ["UJ734797804YP", "UJ730727516YP", "UJ728598353YP", "UJ728598340YP"])
