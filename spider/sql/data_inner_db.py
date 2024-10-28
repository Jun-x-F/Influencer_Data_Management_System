"""
@ProjectName: Influencer_Data_Management_System
@FileName：data_inner_db.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 下午5:22
"""
from sqlalchemy import and_, update, select, delete, func
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
            InfluencersVideoProjectDataByDate.video_url == finish_data.get("video_url"),
            InfluencersVideoProjectDataByDate.updated_at == finish_data.get("updated_at")
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
            InfluencersVideoProjectData.video_url == finish_data.get("video_url")
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


def add_InfluencersVideoProjectData_To_Lock(finish_data):
    try:
        # 开始一个事务
        with db.session.begin_nested():
            # 使用 FOR UPDATE 锁定查询结果，防止其他事务同时读取和修改
            stmt = select(func.max(InfluencersVideoProjectData.parentId)).with_for_update()
            res = db.session.execute(stmt).scalar()
            max_parentId = res if res is not None else 0
            new_parentId = max_parentId + 1
            global_log.info(f"old {max_parentId} -> new {new_parentId}")

            # 为每个数据项设置新的 parentId 并添加到数据库
            for item in finish_data:
                item["parentId"] = new_parentId
                add_data = InfluencersVideoProjectData(**item)
                add_InfluencersVideoProjectData(add_data)

        # 提交事务
        db.session.commit()
        return {'success': True, 'message': 'success'}, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        global_log.error(f"Database error: {e}")
        return {'success': False, 'message': str(e)}, 500

    except Exception as e:
        db.session.rollback()
        global_log.error(f"Unexpected error: {e}")
        return {'success': False, 'message': str(e)}, 500


def add_InfluencersVideoProjectData(finish_data):
    try:
        if not db.check_connection():
            db.reconnect_session()

        # instagram_profile = InfluencersVideoProjectData(
        #     **finish_data
        # )
        db.session.add(finish_data)
        db.session.commit()
    except SQLAlchemyError as e:
        global_log.error(f"Failed to log to database: {e}")
        db.session.rollback()
        raise


def update_InfluencersVideoProjectData(finish_data):
    try:
        if not db.check_connection():
            db.reconnect_session()

        # 提取查询条件
        filters = and_(
            InfluencersVideoProjectData.id == finish_data.get("id")
        )

        db_history_data = (db.session.query(InfluencersVideoProjectData).filter(filters).first())

        if db_history_data:
            db.session.execute(
                update(InfluencersVideoProjectData)
                .where(filters)
                .values(finish_data)
            )
        else:
            raise ValueError(f"Not found Data -> {finish_data}")
        db.session.commit()
    except SQLAlchemyError as e:
        global_log.error(f"Failed to log to database: {e}")
        db.session.rollback()
        raise


def delete_InfluencersVideoProjectData(finish_data, isFilters=True, filters=None):
    try:
        # 检查数据库连接，如果断开则重新连接
        if not db.check_connection():
            db.reconnect_session()

        # 提取查询条件
        if isFilters:
            filters = and_(
                InfluencersVideoProjectData.id == finish_data.get("id")
            )

        # 查询要删除的数据
        db_history_data = db.session.query(InfluencersVideoProjectData).filter(filters).first()

        if db_history_data:
            # 执行删除操作
            db.session.execute(
                delete(InfluencersVideoProjectData)
                .where(filters)
            )
        else:
            raise ValueError(f"未找到要删除的数据 -> {finish_data}")

        # 提交事务
        db.session.commit()
    except SQLAlchemyError as e:
        # 记录错误日志并回滚事务
        global_log.error(f"删除数据库数据失败: {e}")
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
    exists = False
    if db.check_connection() is not True:
        db.reconnect_session()
    filters = and_(
        InfluencersVideoProjectData.id == uniqueId,
        InfluencersVideoProjectData.updated_at >= day_ago
    )
    exists_data = db.session.query(InfluencersVideoProjectData).filter(filters).first()
    if exists_data is not None:
        return exists_data.likes is not None
    return exists


def sync_logistics_information_sheet_to_InfluencersVideoProjectData(logistics_numbers):
    if db.check_connection() is not True:
        db.reconnect_session()
    record = db.session.query(logistics_information_sheet).filter_by(number=logistics_numbers).first()
    global_log.info(f"sync_logistics_information_sheet_to_InfluencersVideoProjectData -> {logistics_numbers},"
                    f" record ->{record}")
    if record is not None:
        existing_records = (db.session.query(InfluencersVideoProjectData).
                            filter(InfluencersVideoProjectData.trackingNumber.like(f"%{record.number}%")).all())
        if existing_records:
            # 更新所有找到的记录
            for existing in existing_records:
                existing.progressLogistics = record.prior_status_zh

            db.session.commit()
            return True
        global_log.error(f"物流信息{logistics_numbers}同步失败...")
    return False


def select_video_urls(select_, filter_, order_, isAll=True):
    if db.check_connection() is not True:
        db.reconnect_session()
    # 使用 SQLAlchemy 的 select 语句进行查询，只获取 URL 字段
    if filter_ is None:
        stmt = select(select_).order_by(order_.desc())
    else:
        stmt = select(select_).filter(filter_).order_by(order_.desc())

    # 执行查询
    if isAll:
        results = db.session.execute(stmt).scalars().all()
    else:
        results = db.session.execute(stmt).scalars().first()
    return results


if __name__ == '__main__':
    print(select_video_urls(select_=func.max(InfluencersVideoProjectData.parentId),
                            filter_=None,
                            order_=InfluencersVideoProjectData.parentId))
