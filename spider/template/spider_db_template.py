"""
数据库表结构
@ProjectName: DataAnalysis
@FileName：spider_db_template.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/25 下午5:33
"""
from datetime import date

from sqlalchemy import Column, Integer, Text, BigInteger, Float, VARCHAR, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# 定义数据模型
# 红人信息表
class CelebrityProfile(Base):
    __tablename__ = 'celebrity_profile'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(VARCHAR(255), nullable=True, comment='用户id')
    platform = Column("平台", VARCHAR(100), nullable=True, comment='媒体平台')
    region = Column("地区", VARCHAR(255), nullable=True, comment='城市')
    country = Column("国家", VARCHAR(255), nullable=True, comment='城市')
    country_code = Column("国家编码", VARCHAR(255), nullable=True, comment='城市')
    level = Column("评级", VARCHAR(100), nullable=True, comment='级别')
    user_name = Column("红人名称", VARCHAR(255), nullable=True, comment='姓名')
    full_name = Column("红人全名", VARCHAR(255), nullable=True, comment='full_name')
    index_url = Column("红人主页地址", Text, nullable=True, comment='红人主页地址')
    profile_picture_url = Column("红人头像地址", Text, nullable=True, comment='头像地址')
    follower_count = Column('粉丝数量', Integer, nullable=True, comment='粉丝数量')
    average_likes = Column('平均点赞数量', Float, nullable=True, comment='平均点赞数量')
    average_comments = Column('平均评论数量', Float, nullable=True, comment='平均评论数量')
    average_views = Column('平均播放量', Float, nullable=True, comment='平均播放量')
    average_engagement_rate = Column('平均参与率', Float, nullable=True, comment='平均参与率')
    email = Column('邮箱', Text, nullable=True, comment='联系方式')
    address1 = Column('地址信息1', Text, nullable=True, comment='地址信息1')
    tag_function1 = Column('标签功能1', VARCHAR(255), nullable=True, comment='标签功能1')
    WhatsApp = Column('WhatsApp', Text, nullable=True, comment='联系方式')
    address2 = Column('地址信息2', Text, nullable=True, comment='地址信息2')
    tag_function2 = Column('标签功能2', VARCHAR(255), nullable=True, comment='标签功能2')
    Discord = Column('Discord', Text, nullable=True, comment='联系方式')
    address3 = Column('地址信息3', Text, nullable=True, comment='地址信息3')
    tag_function3 = Column('标签功能3', VARCHAR(255), nullable=True, comment='标签功能3')
    updated_at = Column('更新日期', Date, default=date.today, onupdate=date.today)


# 视频表
class InfluencersVideoProjectData(Base):
    __tablename__ = 'influencers_video_project_data'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    platform = Column('平台', VARCHAR(255), nullable=True, comment='平台')
    type = Column('类型', VARCHAR(30), nullable=True, comment='数据类型')
    user_name = Column("红人名称", VARCHAR(255), nullable=True, comment='姓名')
    video_url = Column("视频链接", Text, nullable=True, comment='视频链接')
    releasedTime = Column('发布时间', DateTime, nullable=True, comment='发布时间')
    views = Column('播放量', Integer, nullable=True, comment='播放量')
    likes = Column('点赞数', Integer, nullable=True, comment='点赞数')
    comments = Column('评论数', Integer, nullable=True, comment='评论数')
    collections = Column('收藏数', Integer, nullable=True, comment='收藏数')
    forward = Column('转发数', Integer, nullable=True, comment='转发数')
    engagement_rate = Column('参与率', Float, nullable=True, comment='参与率')
    updated_at = Column('更新日期', Date, default=date.today, onupdate=date.today)
    project = Column('项目', VARCHAR(255), nullable=True, comment='项目')
    head = Column('负责人', VARCHAR(255), nullable=True, comment='负责人')
    progressCooperation = Column('合作进度', VARCHAR(255), nullable=True, comment='合作进度')
    progressLogistics = Column('物流进度', VARCHAR(255), nullable=True, comment='物流进度')
    trackingNumber = Column('物流单号', VARCHAR(255), nullable=True, comment='物流单号')
    cost = Column('花费', Integer, nullable=True, comment='花费')
    currency = Column('币种', VARCHAR(30), nullable=True, comment='币种')
    product = Column('产品', VARCHAR(255), nullable=True, comment='产品')
    brand = Column('品牌', VARCHAR(255), nullable=True, comment='品牌')
    estimatedViews = Column('预估观看量', Integer, nullable=True, comment='预估观看量')
    estimatedGoLiveTime = Column('预估上线时间', VARCHAR(255), nullable=True, comment='预估上线时间')
