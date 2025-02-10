"""
@ProjectName: DataAnalysis
@FileName：scheduler_tasks.py
@IDE：PyCharm
@Author：Libre
@Time：2024/10/10 上午10:31
"""
import datetime
import time

from flask import Blueprint
from sqlalchemy import and_

from log.logger import global_log
from log.sendMessage import sendMessage
from spider import run_spider
from spider.spider_threading import extract_tracking_numbers, threading_logistics
from spider.sql.data_inner_db import select_video_urls, inner_InfluencersVideoProjectDataByDate
from spider.template.spider_db_template import CelebrityProfile, InfluencersVideoProjectData, \
    logistics_information_sheet, InfluencersVideoProjectDataByDate
from spider.track.track_spider import run as track_spider

scheduler_task_bp = Blueprint('scheduler_task', __name__)


@scheduler_task_bp.route('/video', methods=['GET'])
def to_update_video_data():
    try:
        res = select_video_urls(InfluencersVideoProjectData.video_url,
                                None,
                                InfluencersVideoProjectData.id)
        global_log.info(f"定时任务 视频信息 -> {res}")
        errorList = []
        warnList = []
        for item in res:
            if item == "" or item is None:
                continue
            global_log.info(item)
            message = run_spider.run_spider(item, {}, 2, "schedule_test")
            if message.get("code") == 500:
                errorList.append(message["message"])
            elif message.get("code") == 404:
                warnList.append(message["message"])
                to_save(item)

        strMessage = ""
        if errorList:
            strMessage += f"## 视频表定期任务\n\n### 重试阶段\n\n**以下链接存在问题**:\n\n" + "\n".join(
                [f"- {url}" for url in errorList])
        # if warnList:
        #     strMessage += f"\n\n***\n\n"
        #     strMessage += f"## 视频表定期任务\n\n### 提醒\n\n**以下链接存在问题**:\n\n" + "\n".join(
        #         [f"- {url}" for url in warnList])
        if strMessage != "":
            sendMessage("视频表定期任务",
                        strMessage)
            return {"status": False, "msg": warnList}
        return {"status": True, "msg": "success"}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


@scheduler_task_bp.route('/celebrity', methods=['GET'])
def to_celebrity_video_data():
    try:
        # 任务实现
        res = select_video_urls(CelebrityProfile.index_url,
                                None,
                                CelebrityProfile.id)
        global_log.info(f"定时任务 红人信息 -> {res}")
        errorList = []
        for item in res:
            if item in ["https://www.instagram.com/raisinghallej/reels/"]:
                continue
            if item == "" or item is None:
                continue
            global_log.info(item)
            message = run_spider.run_spider(item, {}, 1, "schedule_test")
            if message.get("code") == 500:
                errorList.append(message["message"])
            elif message.get("code") == 404:
                errorList.append(message["message"])
                to_save(item)

        if errorList:
            sendMessage("视频表定期任务",
                        f"## 视频表定期任务\n\n### 重试阶段\n\n**以下链接存在问题**:\n\n" + "\n".join(
                            [f"- {url}" for url in errorList]))
            return {"status": False, "msg": errorList}
        return {"status": True, "msg": "success"}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


@scheduler_task_bp.route('/logistics', methods=['GET'])
def to_logistics_data():
    try:
        # 任务实现
        res = select_video_urls(logistics_information_sheet.number,
                                logistics_information_sheet.prior_status != "Delivered",
                                logistics_information_sheet.number)
        trackList = select_video_urls(InfluencersVideoProjectData.trackingNumber,
                                      and_(InfluencersVideoProjectData.trackingNumber != None,
                                           InfluencersVideoProjectData.trackingNumber != "",
                                           InfluencersVideoProjectData.trackingNumber != "test"
                                           ),
                                      InfluencersVideoProjectData.id)
        for track in trackList:
            orderItem = extract_tracking_numbers(track)
            for item in orderItem:
                if item in res:
                    continue
                else:
                    res.append(item)

        #
        global_log.info(f"定时任务 物流信息 -> {res}")
        returnRes = False
        info = None
        for _ in range(5):
            returnRes, info = track_spider(True, res)
            if returnRes:
                break
            else:
                time.sleep(2)

        threading_logistics.set()
        # for item in res:
        #     res = sync_logistics_information_sheet_to_InfluencersVideoProjectData(item)
        #     global_log.info(f"同步情况 {res}")
        return {"status": returnRes, "msg": info}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


def to_save(url):
    result: InfluencersVideoProjectData = select_video_urls(select_=InfluencersVideoProjectData,
                                                            filter_=InfluencersVideoProjectData.video_url == url,
                                                            order_=InfluencersVideoProjectData.parentId)[0]
    # InfluencersVideoProjectDataByDate(**result)
    from sqlalchemy import inspect

    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    result_toDict = object_as_dict(result)
    del result_toDict["id"]
    # 获取 InfluencersVideoProjectDataByDate 的键集合
    data_by_date_keys = set(object_as_dict(InfluencersVideoProjectDataByDate()).keys())

    # 过滤 result_toDict，只保留 data_by_date_keys 中的键
    filtered_result = {key: result_toDict[key] for key in data_by_date_keys if key in result_toDict}
    filtered_result["updated_at"] = datetime.date.today()
    print(result_toDict)
    print(filtered_result)
    inner_InfluencersVideoProjectDataByDate(filtered_result)


def to_update_video_data_to_retry():
    try:
        res =  [
            "https://www.instagram.com/reel/DEC93mcgd4S/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.tiktok.com/@zalginnireels/video/7452953325416353032?is_from_webapp=1&sender_device=pc&web_id=7416526875147732522",
            "https://www.instagram.com/reel/DDu_EXWyA2l/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.tiktok.com/@jayhym/video/7449859121832152362?is_from_webapp=1&web_id=7336270110263707178",
            "https://www.instagram.com/reel/DDudDO1u2mp/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.youtube.com/watch?v=cW9ScPnwXME",
            "https://www.tiktok.com/@wissofpv/video/7447839961576934689",
            "https://www.instagram.com/reel/DDczL7KsxLr/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/p/DDcFqo9IfIJ/",
            "https://www.tiktok.com/@cozy.eleanor/video/7445758287754054944?is_from_webapp=1&sender_device=pc&web_id=7416526875147732522",
            "https://www.instagram.com/reel/DC6pT-UMx89/",
            "https://www.instagram.com/reel/DCT8HqrI8vJ/",
            "https://www.instagram.com/reel/DCZd_ZexPRd/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/DB_srLDoj4Z/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.tiktok.com/@amira.benghanem/video/7429352386537262369",
            "https://www.instagram.com/reel/DDEBn5MNEiW/",
            "https://www.instagram.com/reel/DClkF8gArtD/",
            "https://www.tiktok.com/@fionasbishop/video/7428155062809054496?is_from_webapp=1&sender_device=pc&web_id=7416526875147732522",
            "https://www.instagram.com/reel/C-7hPa6NESp/?igsh=bWloYTFwOXBydWZw",
            "https://www.tiktok.com/@sasha.mints/video/7424780632779148587",
            "https://www.tiktok.com/@jjadavitt/video/7427240156899331358?is_from_webapp=1&sender_device=pc&web_id=7416526875147732522",
            "https://www.instagram.com/reel/C-7hPa6NESp/?igsh=bWloYTFwOXBydWZw",
            "https://www.instagram.com/reel/DChU49FNhCF/",
            "https://www.instagram.com/reel/DC7GSbWttMW/",
            "https://www.instagram.com/p/C-uAo_4uvWe/?img_index=1",
            "https://www.instagram.com/reel/C-fDqFwgR9p/",
            "https://www.instagram.com/reel/C_izJ-tPAUI/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C-wYVB7RHJk/?igsh=MW94NmZ5eG5hazdsdg%3D%3D",
            "https://www.tiktok.com/@alexistinsay/video/7402845808552381703?is_from_webapp=1&sender_device=pc&web_id=7362060442637059614",
            "https://www.tiktok.com/@fionasbishop/video/7413320597054278945",
            "https://www.instagram.com/reel/C-mdQ-tszcA/?igsh=bW5sOGNodHp4M2p5",
            "https://www.tiktok.com/@elindaviess2/video/7411411180624891168?is_from_webapp=1&sender_device=pc&web_id=7376948677829985835",
            "https://www.tiktok.com/@bentleyyy.s/video/7402718877978774815?is_from_webapp=1&sender_device=pc&web_id=7376948677829985835",
            "https://www.instagram.com/reel/C4chaKoRPKc/",
            "https://www.instagram.com/reel/C4dWaUNLaTS/",
            "https://www.instagram.com/reel/C40TfertqL_/",
            "https://www.instagram.com/p/DAG8ezESf4u/",
            "https://www.instagram.com/p/C-wC4vrRw4y/",
            "https://www.tiktok.com/@moms_besties/video/7416201877228014855?is_from_webapp=1&sender_device=pc&web_id=7416526875147732522",
            "https://www.instagram.com/reel/C2q_hMArrKS/",
            "https://www.tiktok.com/@thejunglebadger/video/7395298474658516257",
            "https://www.instagram.com/reel/C7bpmEcMRMu/",
            "https://www.instagram.com/reel/C909nZBO7AW/?igsh=MTNscml2am80amo2cQ==",
            "https://www.instagram.com/reel/C97OGqeS90J/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C882MXts6Gc/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C86TSXNMXUm/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.tiktok.com/@jjadavitt/video/7381460381979495726?_r=1&_t=8nI4sHD6pgd",
            "https://www.instagram.com/reel/C7goYbHM91t/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7fMSZeMkY9/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7escZdMeuk/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7WhOhcymbl/?utm_source=ig_web_copy_link",
            "https://www.instagram.com/reel/C7jM7fsoakv/?utm_source=ig_web_copy_link",
            "https://www.instagram.com/reel/C7T-AaTRkIP/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7LoaZSsjt9/?igsh=MWpjOHAwZXF2enVtcQ==",
            "https://www.instagram.com/reel/C7W4suzMf4Y/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7KTaZrr-QW/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7RwfgQMZ9N/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7PSr5xMpVb/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7ReXvcsddG/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C7jQyHwMD33/?utm_source=ig_web_copy_link",
            "https://www.instagram.com/reel/C7Wj4fhMGgU/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
            "https://www.instagram.com/reel/C8K5VBFycqX/",
            "https://www.instagram.com/reel/C8xFIElMJoT/",
            "https://www.instagram.com/p/C7eAAICtXyP/",
            "https://www.instagram.com/reel/C8B_61Ts6kH/",
            "https://www.instagram.com/p/C7raR8jIk3a/",
            "https://www.instagram.com/p/C7Ojk_Syrg6/",
            "https://www.instagram.com/reel/C6yMBY0yb0S/",
            "https://www.instagram.com/reel/C6Y53_OPjtb/",
            "https://www.instagram.com/reel/C7ROsVnib_z/",
            "https://www.instagram.com/reel/C6Zj4U4ttb-/",
            "https://www.instagram.com/p/C6lNV2GyqAw/",
            "https://www.instagram.com/p/C6wBSCbAvM6/",
            "https://www.tiktok.com/@imaeternal/video/7351250438076796165",
            "https://www.instagram.com/p/C4gLrTrglA-/",
            "https://www.instagram.com/reel/C4dX5q0N18V/",
            "https://www.instagram.com/reel/C55fzb6xLxo/?igsh=eWh0c3Y1Z2ZwdGJ2",
            "https://www.instagram.com/reel/C6EXUIcREt4/",
            "https://www.instagram.com/reel/C6QzjRYtx_f/",
            "https://www.instagram.com/reel/C4dFoI5Lwn5/",
            "https://www.instagram.com/reel/C2uhtuuuYB5/",
            "https://www.tiktok.com/@jonimperial/video/7329921853848341803",
            "https://www.tiktok.com/@nvzion/video/7329897303903554862",
            "https://www.instagram.com/reel/C2uhywOAQPX/",
            "https://www.tiktok.com/@bbbigdeer/video/7329382270496804139",
            "https://www.instagram.com/reel/C2ugXZgORUK/"
        ]
        global_log.info(f"定时任务 视频信息 -> {res}")
        errorList = []
        warnList = []
        for item in res:
            if item == "" or item is None:
                continue
            global_log.info(item)
            message = run_spider.run_spider(item, {}, 2, "schedule_test")
            if message.get("code") == 500:
                errorList.append(message["message"])
            elif message.get("code") == 404:
                warnList.append(message["message"])
                to_save(item)
        strMessage = ""
        if errorList:
            strMessage += f"## 视频表定期任务\n\n### 重试阶段\n\n**以下链接存在问题**:\n\n" + "\n".join(
                [f"- {url}" for url in errorList])
        if warnList:
            strMessage += f"\n\n***\n\n"
            strMessage += f"## 视频表定期任务\n\n### 提醒\n\n**以下链接存在问题**:\n\n" + "\n".join(
                [f"- {url}" for url in warnList])
        if strMessage != "":
            sendMessage("视频表定期任务",
                        strMessage)
            return {"status": False, "msg": warnList}
        return {"status": True, "msg": "success"}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


def to_celebrity_video_data_to_retry():
    try:
        # 任务实现
        res = [
            "https://www.youtube.com/@LainaAndKing",
            "https://www.youtube.com/@JediMasterBinkz"
        ]
        global_log.info(f"定时任务 红人信息 -> {res}")
        errorList = []
        for item in res:
            if item in ["https://www.instagram.com/raisinghallej/reels/"]:
                continue
            if item == "" or item is None:
                continue
            global_log.info(item)
            message = run_spider.run_spider(item, {}, 1, "schedule_test")
            if message.get("code") == 500:
                errorList.append(message["message"])
            elif message.get("code") == 404:
                errorList.append(message["message"])
                # to_save(item)

        if errorList:
            sendMessage("视频表定期任务",
                        f"## 视频表定期任务\n\n### 重试阶段\n\n**以下链接存在问题**:\n\n" + "\n".join(
                            [f"- {url}" for url in errorList]))
            return {"status": False, "msg": errorList}
        return {"status": True, "msg": "success"}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


if __name__ == '__main__':
    to_update_video_data_to_retry()
    # to_update_video_data_to_retry()
