"""
@ProjectName: Influencer_Data_Management_System
@FileName：data_inner_db.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 下午5:22
"""
from sqlalchemy import and_, update
from sqlalchemy.exc import SQLAlchemyError

from log.logger import global_log
from spider.sql.mysql import Connect
from spider.template.spider_db_template import Base, InfluencersVideoProjectDataByDate, CelebrityProfile, \
    InfluencersVideoProjectData, logistics_information_sheet

db = Connect(2, "marketing")
db.create_session()
Base.metadata.create_all(db.engine)

global_log.info("数据库: marketing 链接成功")


def inner_InfluencersVideoProjectDataByDate(finish_data):
    try:
        if not db.check_connection():
            db.reconnect_session()

        # 提取查询条件
        filters = and_(
            InfluencersVideoProjectDataByDate.platform == finish_data.get("platform"),
            InfluencersVideoProjectDataByDate.user_name == finish_data.get("user_name"),
            InfluencersVideoProjectDataByDate.updated_at == finish_data.get("updated_at"),
        )

        # 检查是否已有记录
        db_history_data = db.session.query(InfluencersVideoProjectDataByDate).filter(filters).first()

        if db_history_data:
            # 如果记录存在，则更新
            db.session.execute(
                update(InfluencersVideoProjectDataByDate)
                .where(filters)
                .values(finish_data)
            )
        else:
            # 如果记录不存在，则插入新记录
            new_record = InfluencersVideoProjectDataByDate(**finish_data)
            db.session.add(new_record)

        db.session.commit()

    except SQLAlchemyError as e:
        global_log.error(f"Failed to log to database: {e}")
        db.session.rollback()
        raise


def inner_InfluencersVideoProjectData(finish_data):
    try:
        if not db.check_connection():
            db.reconnect_session()

        # 提取查询条件
        filters = and_(
            InfluencersVideoProjectData.platform == finish_data.get("platform"),
            InfluencersVideoProjectData.user_name == finish_data.get("user_name"),
        )

        db_history_data = (db.session.query(InfluencersVideoProjectData).filter(filters).first())

        if db_history_data:
            db.session.execute(
                update(InfluencersVideoProjectData)
                .where(filters)
                .values(finish_data)
            )
        else:
            instagram_profile = InfluencersVideoProjectData(
                **finish_data
            )
            db.session.add(instagram_profile)
        db.session.commit()
    except SQLAlchemyError as e:
        global_log.error(f"Failed to log to database: {e}")
        db.session.rollback()
        raise


def inner_CelebrityProfile(finish_data, isById=False):
    try:
        if db.check_connection() is not True:
            db.reconnect_session()

        # 提取查询条件
        if isById is True:
            filters = and_(
                CelebrityProfile.platform == finish_data.get("platform"),
                CelebrityProfile.user_id == finish_data.get("user_id"),
            )
        else:
            filters = and_(
                CelebrityProfile.platform == finish_data.get("platform"),
                CelebrityProfile.user_name == finish_data.get("user_name"),
            )

        db_history_data = (db.session.query(CelebrityProfile).filter(filters).first())
        if db_history_data:
            db.session.execute(update(CelebrityProfile).where(filters).values(finish_data))
        else:
            instagram_profile = CelebrityProfile(
                **finish_data
            )
            db.session.add(instagram_profile)
        db.session.commit()
    except SQLAlchemyError as e:
        global_log.error(f"Failed to log to database: {e}")
        db.session.rollback()
        raise


def check_InfluencersVideoProjectData_in_db(uniqueId, day_ago) -> bool:
    if db.check_connection() is not True:
        db.reconnect_session()
    filters = and_(
        InfluencersVideoProjectData.id == uniqueId,
        InfluencersVideoProjectData.updated_at >= day_ago
    )
    exists = db.session.query(InfluencersVideoProjectData).filter(filters).first() is not None
    return exists


def sync_logistics_information_sheet_to_InfluencersVideoProjectData(logistics_numbers):
    if db.check_connection() is not True:
        db.reconnect_session()
    record = db.session.query(logistics_information_sheet).filter_by(number=logistics_numbers).first()
    if record is not None:
        existing_records = db.session.query(InfluencersVideoProjectData).filter_by(trackingNumber=record.number).all()
        if existing_records:
            # 更新所有找到的记录
            for existing in existing_records:
                existing.progressLogistics = record.prior_status_zh

            db.session.commit()
            return True
    return False
