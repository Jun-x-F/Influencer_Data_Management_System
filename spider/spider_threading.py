"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_threading.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午5:44
"""
import threading
import time
from collections import deque

from sqlalchemy import and_

from log.logger import global_log
from spider import run_spider
from spider.config.config import order_links, message_queue
from spider.config.request_config import RequestConfig, TaskStatus
from spider.sql.data_inner_db import select_video_urls, \
    sync_logistics_information
from spider.template.class_dict_template import FIFODict
from spider.template.spider_db_template import logistics_information_sheet, InfluencersVideoProjectData
from spider.track.track_spider import run as track_spider

threading_influencersVideo = threading.Event()
threading_logistics = threading.Event()


def extract_tracking_numbers(text: str):
    # Regular expression pattern to match tracking numbers like UJ712686735YP
    # https://t.17track.net/zh-cn#nums=QL0500152802211YQ
    text = text.strip()
    parentText: str = text.replace('https://t.17track.net/zh-cn#nums=', '')

    # pattern = r'[A-Z]{2}\d{9}[A-Z]{2}'
    # # Find all occurrences of the pattern in the text
    # tracking_numbers = re.findall(pattern, text)
    return parentText.split(",")


def process_links(_queue: FIFODict, flag: int) -> None:
    """
    公共代码，执行任务，传入的_queue不是同一个
    可能存在有物流订单但是没有视频链接的问题，需要进行判断
    优先缓存3秒，保证流程执行完毕之后才进行其他操作
    """
    # 忙等待
    time.sleep(2)
    send_id = None
    message = None
    error_links_list = []
    success_links_list = []
    success_order_list = []
    error_order_list = []

    # 红人
    if flag == 1:
        if not _queue or _queue.is_empty():
            return
        send_id, links = _queue.dequeue()
        for link in links:
            message = run_spider.run_spider(link, {}, flag, send_id)
            if message.get("code") == 500:
                error_links_list.append(link)
            elif message.get("code") == 200:
                success_links_list.append(link)
    # 视频
    elif flag == 2:
        if _queue.is_empty() and order_links.is_empty():
            return

        if not _queue.is_empty() and _queue:
            send_id, links = _queue.dequeue()

            for link in links:
                message = run_spider.run_spider(link, {}, flag, send_id)
                if message.get("code") == 500:
                    error_links_list.append(link)
                elif message.get("code") == 200:
                    success_links_list.append(link)

            if len(error_links_list) > 0:
                message_queue.add(send_id, f"执行失败链接: {error_links_list}", "error")
            else:
                message_queue.add(send_id, f"获取视频信息结果 成功")

    if send_id is not None:
        order_links_deque: deque = order_links.pop(send_id)
        global_log.info(f"order_links_deque-> {order_links_deque}")
    else:
        send_id, order_links_deque = order_links.dequeue()
        global_log.info(f"order_links_deque-> {order_links_deque}")

    if order_links_deque is not None:
        for order_link in order_links_deque:
            order_ls = extract_tracking_numbers(order_link.strip())
            global_log.info(f"提取出来物流信息为{order_ls}, 开始执行")
            message_queue.add(send_id, f"开始获取物流信息，物流单号为 {order_ls}")
            res = False
            res_message = None
            for _ in range(3):
                res, res_message = track_spider(isRequest=True, order_numbers=order_ls)
                if res is True:
                    break
                message_queue.add(send_id, f"重试获取物流信息，原因：网络问题...")
                time.sleep(3)
            message_queue.add(send_id, f"获取物流信息结果为{'成功' if res is True else res_message}...")
            if res is False:
                error_order_list.append(order_link)
                global_log.info("任务: 同步物流信息跳过, 原因获取物流信息报错...")
            else:
                success_order_list.append(order_link)
            #     for order in order_ls:
            #         res = sync_logistics_information_sheet_to_InfluencersVideoProjectData(order)
            #         global_log.info(f"任务：同步物流信息 -> {res}")
        threading_logistics.set()
    if len(error_links_list) > 0:
        message_queue.add(send_id, f"以下链接都失败了\n{error_links_list}", status="error")
    elif len(error_order_list) > 0:
        message_queue.add(send_id, f"以下物流链接都失败了\n{error_order_list}", status="error")
    else:
        message_queue.add(send_id, "成功", status="finish")
    # message_queue.to_end(send_id)
    global_log.info(
        f"本次执行结果: \n成功链接共有\n{success_links_list}\n成功物流链接共有\n{success_order_list}\n失败链接共有\n{error_links_list}\n失败物流链接共有\n{error_order_list}")


def process_task_with_retry(task_id: str, process_func, max_retries: int = 3) -> bool:
    """
    使用重试机制处理任务
    
    Args:
        task_id: 任务ID
        process_func: 处理函数，返回格式为 {"code": int, "message": str}
        max_retries: 最大重试次数
        
    Returns:
        bool: 任务是否成功
    """
    try:
        # 更新任务状态为运行中
        RequestConfig.update_task_status(task_id, TaskStatus.RUNNING)
        
        retries = 0
        while retries < max_retries:
            try:
                # 执行任务并获取结果
                result = process_func()
                
                # 解析返回结果
                if isinstance(result, dict) and "code" in result:
                    if result["code"] == 200:
                        # 任务成功，更新状态为完成
                        RequestConfig.update_task_status(task_id, TaskStatus.COMPLETED)
                        return True
                    else:
                        # 任务失败，记录错误信息
                        error_message = result.get("message", "未知错误")
                        global_log.error(f"任务执行失败: {error_message}")
                        retries += 1
                        if retries < max_retries:
                            time.sleep(3)  # 重试前等待3秒
                            global_log.info(f"正在进行第{retries}次重试...")
                        continue
                else:
                    raise ValueError("处理函数返回格式不正确")
                
            except Exception as e:
                global_log.error(f"任务执行失败: {str(e)}")
                retries += 1
                if retries < max_retries:
                    time.sleep(3)  # 重试前等待3秒
                    global_log.info(f"正在进行第{retries}次重试...")
        
        # 超过最大重试次数，更新状态为失败
        error_message = result.get("message", f"重试{max_retries}次后失败") if isinstance(result, dict) else f"重试{max_retries}次后失败"
        RequestConfig.update_task_status(task_id, TaskStatus.FAILED, error_message)
        return False
        
    except Exception as e:
        global_log.error(f"任务状态更新失败: {str(e)}")
        RequestConfig.update_task_status(task_id, TaskStatus.FAILED, str(e))
        return False

def process_influencer_tasks():
    """处理红人任务"""
    while True:
        try:
            # 获取红人任务
            tasks = RequestConfig.get_influencer_tasks("红人")
            task_list = tasks.get("tasks")
            if task_list and isinstance(task_list, list):
                for task in task_list:
                    task_id = task.get('task_id')
                    task_url = task.get('task_url')
                    if task_id:
                        def process_func():
                            # 这里添加处理红人任务的具体逻辑
                            message = run_spider.run_spider(task_url, {}, 1, "spider_system")
                            return message
                        process_task_with_retry(task_id, process_func)
        except Exception as e:
            global_log.error(f"处理红人任务失败: {str(e)}")
        finally:
            time.sleep(35)

def process_video_tasks():
    """处理视频任务"""
    while True:
        try:
            # 获取视频任务
            tasks = RequestConfig.get_influencer_tasks("视频")
            task_list = tasks.get("tasks")
            if task_list and isinstance(task_list, list):
                for task in task_list:
                    task_id = task.get('task_id')
                    task_url = task.get('task_url')
                    if task_id:
                        def process_func():
                            # 这里添加处理视频任务的具体逻辑
                            message = run_spider.run_spider(task_url, {}, 2, "spider_system")
                            return message
                        process_task_with_retry(task_id, process_func)
        except Exception as e:
            global_log.error(f"处理视频任务失败: {str(e)}")
        finally:
            time.sleep(35)

def process_logistics_tasks():
    """处理物流任务"""
    while True:
        try:
            # 获取物流任务
            tasks = RequestConfig.get_influencer_tasks("物流")
            task_list = tasks.get("tasks")
            if task_list and isinstance(task_list, list):
                for task in task_list:
                    task_id = task.get('task_id')
                    task_url = task.get('task_url')
                    if task_id:
                        def process_func():
                            # 这里添加处理物流任务的具体逻辑
                            order_ls = extract_tracking_numbers(task_url.strip())
                            res, res_message = track_spider(isRequest=True, order_numbers=order_ls)
                            return {"code": 200 if res is True else 500, "message": res_message}
                        process_task_with_retry(task_id, process_func)
        except Exception as e:
            global_log.error(f"处理物流任务失败: {str(e)}")
        finally:
            time.sleep(35)

def cleanNoneNotice():
    """删除超时的队列信息"""
    while True:
        expired_list = message_queue.is_expired()
        for expired_item in expired_list:
            message_queue.delete(expired_item)
        time.sleep(10)


def syncLogisticsDataBase():
    """同步物流信息的队列"""
    sync_mapping = {}
    xxx = set()
    while True:
        try:
            if threading_logistics.is_set():
                # 忙加载，等待1分钟后开始同步
                time.sleep(60 * 1)
                res = select_video_urls(logistics_information_sheet,
                                        None,
                                        logistics_information_sheet.number)
                cur_obj = {}
                for item in res:
                    cur_obj[item.number] = item.prior_status_zh

                trackList = select_video_urls(InfluencersVideoProjectData.trackingNumber,
                                              and_(InfluencersVideoProjectData.trackingNumber != None,
                                                   InfluencersVideoProjectData.trackingNumber != "",
                                                   InfluencersVideoProjectData.trackingNumber != "test"
                                                   ),
                                              InfluencersVideoProjectData.id)
                toData = []
                for track in trackList:
                    if "t.17track.net" not in track:
                        continue
                    if track in xxx or track in sync_mapping.keys():
                        continue
                    else:
                        xxx.add(track)
                    obj = {
                        "trackingNumber": track,
                    }
                    # progressLogistics
                    for key, value in cur_obj.items():
                        if key in track:
                            cur_value = obj.get("progressLogistics", None)
                            if cur_value is None:
                                obj["progressLogistics"] = value
                                continue

                            if cur_value != value and cur_value == "运输途中":
                                continue
                            else:
                                if value in ["交付",
                                             "到达待取",
                                             "成功签收"]:
                                    sync_mapping[track] = sync_mapping.get(track, 0) + 1
                                obj["progressLogistics"] = value
                    res = sync_logistics_information(obj)
                    global_log.info(f"{track}，{res}")
                    toData.append(obj)
                # for item in toData:
                #     res = sync_logistics_information(item)
                #     global_log.info(f"{item}，{res}")
                # global_log.info(sync_logistics_information(item))
                threading_logistics.clear()
        except Exception:
            global_log.error()
        finally:
            # 每10s判断一次
            time.sleep(10)


if __name__ == '__main__':
    # 创建并启动三个任务处理线程
    influencer_thread = threading.Thread(target=process_influencer_tasks, daemon=True)
    video_thread = threading.Thread(target=process_video_tasks, daemon=True)
    logistics_thread = threading.Thread(target=process_logistics_tasks, daemon=True)
    
    influencer_thread.start()
    video_thread.start()
    logistics_thread.start()
    
    # 启动其他必要的线程
    clean_thread = threading.Thread(target=cleanNoneNotice, daemon=True)
    clean_thread.start()
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在退出程序...")
