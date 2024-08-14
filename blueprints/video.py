import datetime
import re
from collections import deque

import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import text

from base import ReadDatabase, DF_ToSql, DatabaseUpdater
from spider.template.class_dict_template import FIFODict
from utils import determine_platform

video_bp = Blueprint('video', __name__)

# 用于存储用户提交的视频链接
submitted_video_links = FIFODict()

class Video:
    @staticmethod
    @video_bp.route('/get_platforms', methods=['GET'])
    def get_platforms():
        try:
            DATABASE = 'marketing'
            sql = 'SELECT DISTINCT 平台 FROM celebrity_profile'
            current_app.logger.info(f"执行SQL查询: {sql}")
            platforms_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {platforms_df}")
            platforms = platforms_df['平台'].tolist()
            return jsonify({'platforms': platforms}), 200
        except Exception as e:
            current_app.logger.error(f"获取平台信息失败: {e}")
            return jsonify({'message': f'获取平台信息失败: {e}'}), 500

    @staticmethod
    @video_bp.route('/get_influencers', methods=['POST'])
    def get_influencers():
        try:
            data = request.json
            platform = data.get('platform')
            DATABASE = 'marketing'
            sql = f"SELECT 红人名称 FROM celebrity_profile WHERE 平台='{platform}'"
            current_app.logger.info(f"执行SQL查询: {sql}")
            influencers_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {influencers_df}")
            influencers = influencers_df['红人名称'].tolist()
            return jsonify({'influencers': influencers}), 200
        except Exception as e:
            current_app.logger.error(f"获取红人信息失败: {e}")
            return jsonify({'message': f'获取红人信息失败: {e}'}), 500

    @staticmethod
    @video_bp.route('/get_project_info', methods=['GET'])
    def get_project_info():
        try:
            DATABASE = 'marketing'
            sql = 'SELECT DISTINCT 品牌,项目, 负责人 FROM influencers_video_project_data'
            current_app.logger.info(f"执行SQL查询: {sql}")
            project_info_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {project_info_df}")

            # 替换 NaN 或 None 值
            project_info_df = project_info_df.fillna('')

            brand = project_info_df['品牌'].tolist()
            projects = project_info_df['项目'].tolist()
            managers = project_info_df['负责人'].tolist()


            return jsonify({'brand': brand,'projects': projects, 'managers': managers}), 200
        except Exception as e:
            current_app.logger.error(f"获取项目信息失败: {e}")
            return jsonify({'message': f'获取项目信息失败: {e}'}), 500

    @staticmethod
    @video_bp.route('/get_unique_ids', methods=['GET'])
    def get_unique_ids():
        try:
            DATABASE = 'marketing'
            sql = 'SELECT id FROM influencers_video_project_data'
            current_app.logger.info(f"执行SQL查询: {sql}")
            unique_ids_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {unique_ids_df}")

            unique_ids = unique_ids_df['id'].tolist()
            return jsonify({'uniqueIds': unique_ids}), 200
        except Exception as e:
            current_app.logger.error(f"获取唯一ID失败: {e}")
            return jsonify({'message': f'获取唯一ID失败: {e}'}), 500

    @staticmethod
    @video_bp.route('/get_project_and_manager', methods=['POST'])
    def get_project_and_manager():
        try:
            data = request.json
            unique_id = data.get('uniqueId')
            DATABASE = 'marketing'
            sql = f"SELECT 品牌, 项目, 负责人 FROM influencers_video_project_data WHERE id='{unique_id}'"
            current_app.logger.info(f"执行SQL查询: {sql}")
            result_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {result_df}")

            if not result_df.empty:
                brand = result_df['品牌'].iloc[0] if pd.notna(result_df['品牌'].iloc[0]) else ''
                project = result_df['项目'].iloc[0] if pd.notna(result_df['项目'].iloc[0]) else ''
                manager = result_df['负责人'].iloc[0] if pd.notna(result_df['负责人'].iloc[0]) else ''
                return jsonify({'brand': brand, 'project': project, 'manager': manager}), 200
            else:
                return jsonify({'message': '未找到匹配的项目、品牌和负责人信息'}), 404
        except Exception as e:
            current_app.logger.error(f"获取项目、品牌和负责人信息失败: {e}")
            return jsonify({'message': f'获取项目、品牌和负责人信息失败: {e}'}), 500

    @staticmethod
    @video_bp.route('/get_video_data', methods=['GET'])
    def get_video_data():
        DATABASE = 'marketing'
        sql_t = 'influencers_video_project_data'
        try:
            data = ReadDatabase(DATABASE, f'SELECT * FROM {sql_t}').vm()  # 假设 ReadDatabase 函数返回的是 DataFrame
            # 处理空值和特殊值
            # 处理 NaN 和 inf 值
            data = data.replace({float('nan'): None, float('inf'): None, float('-inf'): None})

            # 将 DataFrame 转换为字典列表
            result = data.to_dict(orient='records')  # 将 DataFrame 转换为字典列表
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @video_bp.route('/submit_link', methods=['POST'])
    def submit_link():
        try:
            data = request.json
            link = data.get('link')
            unique_id = data.get('uniqueId')
            project_name = data.get('projectName')
            brand = data.get('brand')
            manager = data.get('manager')
            progress = data.get('progress')
            logistics_number = data.get('logisticsNumber')
            cost = data.get('cost')
            currency = data.get('currency')  # 接收币种
            product = data.get('product')
            estimated_views = data.get('estimatedViews')
            estimated_launch_date = data.get('estimatedLaunchDate')
            send_id = data.get('send_id')

            # 链接可以为空，如果存在则进行验证
            if link:
                url_pattern = re.compile(r'^(http|https)://')
                if not url_pattern.match(link):
                    return jsonify({'message': '无效的URL格式。'}), 400

                # Determine platform based on URL
                platform_from_link = determine_platform(link)
                if not platform_from_link:
                    return jsonify({'message': '不支持的平台。'}), 400

                # Add submitted_video_links link
                send_id_links: deque = submitted_video_links.get(send_id, deque())
                if link in send_id_links:
                    return jsonify({'message': f'链接{link} 存在队列中, 请勿重复生成任务'}), 200
                send_id_links.append(link)
                submitted_video_links[send_id] = send_id_links

            # Collect data to DataFrame
            video_data = {
                'id': [unique_id],
                '品牌': [brand],
                '项目': [project_name],
                '负责人': [manager],
                '合作进度': [progress],
                '物流单号': [logistics_number],
                '花费': [cost],
                '币种': [currency],  # 添加币种
                '产品': [product],
                '预估观看量': [estimated_views],
                '预估上线时间': [estimated_launch_date],
                '视频链接': [link],
                '更新日期': [datetime.date.today()]
            }

            update_date = datetime.date.today()
            video_data['更新日期'] = update_date
            df = pd.DataFrame(video_data)
            # 删除空列
            df.replace('', pd.NA, inplace=True)
            df = df.dropna(axis=1, how='all')

            # 定义索引字段
            index_fields = ['id']

            # 检查表是否存在
            DATABASE = 'marketing'
            sql_t = 'influencers_video_project_data'
            try:
                existing_data = ReadDatabase(DATABASE, f'select * from {sql_t}').vm()
                table_exists = not existing_data.empty
            except Exception as e:
                table_exists = False

            if not table_exists:
                # 表不存在，创建表并插入数据
                tosql_if_exists = 'replace'
                DF_ToSql(df, DATABASE, sql_t, tosql_if_exists).mapping_df_types().add_index(index_fields, index_type='UNIQUE')
            else:
                # 表存在，检查索引是否存在
                try:
                    index_info = ReadDatabase(DATABASE, f"SHOW INDEX FROM {sql_t} WHERE Key_name='idx_{sql_t}_unique'").vm()
                    index_exists = not index_info.empty
                except Exception as e:
                    index_exists = False

                if not index_exists:
                    # 索引不存在，创建索引
                    create_index_sql = f"CREATE UNIQUE INDEX idx_{sql_t}_unique ON {sql_t} ({', '.join(index_fields)});"
                    try:
                        db_updater = DatabaseUpdater()
                        engine = db_updater.vm_marketing
                        with engine.connect() as connection:
                            connection.execute(text(create_index_sql))
                        print(f"索引 idx_{sql_t}_unique 创建成功。")
                    except Exception as e:
                        print(f"创建索引失败: {e}")

                # 更新现有表中的数据
                db_updater = DatabaseUpdater()
                db_updater.update_database_batched(db_updater.vm_marketing, sql_t, df, index_fields)
                print('更新开始时间', datetime.datetime.now())
                print('更新结束时间', datetime.datetime.now())
                print('更新的数据日期', update_date)

            return jsonify({'message': '项目信息提交成功。'}), 200

        except Exception as e:
            current_app.logger.error(f"内部服务器错误: {e}")
            return jsonify({'message': '内部服务器错误。'}), 500

    @staticmethod
    @video_bp.route('/add_video_data', methods=['POST'])
    def add_video_data():
        DATABASE = 'marketing'
        sql_t = 'influencers_video_project_data'
        try:
            data = request.json  # 假设你是通过 JSON 发送数据
            brand = data.get('品牌')
            project_name = data.get('项目')
            manager = data.get('负责人')
            cost = data.get('花费')
            product = data.get('产品')
            ProgressCooperation = data.get('合作进度')
            estimatedViews = data.get('预估观看量')
            estimatedLaunchDate = data.get('预估上线时间')

            # 处理空字符串，将其转换为 None
            video_data = {
                '品牌': [brand or None],
                '项目': [project_name or None],
                '负责人': [manager or None],
                '花费': [cost or None],
                '产品': [product or None],
                '合作进度': [ProgressCooperation or None],
                '预估观看量': [estimatedViews or None],
                '预估上线时间': [estimatedLaunchDate or None]
            }
            update_date = datetime.date.today()
            video_data['更新日期'] = update_date
            df = pd.DataFrame(video_data)
            # 添加缺失的列，初始化为空值
            all_columns = ['id', '平台', '类型', '红人名称', '发布时间', '播放量', '点赞数', '评论数', '收藏数', '转发数', '参与率','视频链接'
                           '更新日期','品牌', '项目', '负责人', '合作进度', '物流进度', '物流单号', '花费', '产品', '预估观看量', '预估上线时间']
            # 将缺失的列添加到 DataFrame 中，并将其初始化为 None（或 np.nan）
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None
            # 确保列的顺序与 `all_columns` 一致（可选）
            df = df[all_columns]
            print(data)
            tosql_if_exists = 'append'
            DF_ToSql(df, DATABASE, sql_t, tosql_if_exists).mapping_df_types()
            return jsonify({'message': '数据添加成功'}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500

