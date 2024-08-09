import datetime
import re

import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import text

from base import ReadDatabase, DF_ToSql, DatabaseUpdater
from utils import determine_platform

video_bp = Blueprint('video', __name__)

# 用于存储用户提交的视频链接
submitted_video_links = {}

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
            sql = 'SELECT DISTINCT 项目, 负责人, 花费, 产品 FROM influencers_video_project_data'
            current_app.logger.info(f"执行SQL查询: {sql}")
            project_info_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {project_info_df}")
            projects = project_info_df['项目'].tolist()
            managers = project_info_df['负责人'].tolist()
            costs = project_info_df['花费'].tolist()
            products = project_info_df['产品'].tolist()
            return jsonify({'projects': projects, 'managers': managers, 'costs': costs, 'products': products}), 200
        except Exception as e:
            current_app.logger.error(f"获取项目信息失败: {e}")
            return jsonify({'message': f'获取项目信息失败: {e}'}), 500

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
            print(data)
            link = data.get('link')
            platform = data.get('platform')
            influencer_name = data.get('influencerName')
            project_name = data.get('projectName')
            manager = data.get('manager')
            cost = data.get('cost')
            product = data.get('product')
            send_id = data.get('send_id')

            # Validate input
            if not link:
                return jsonify({'message': '链接是必需的。'}), 400

            # Validate URL format
            url_pattern = re.compile(r'^(http|https)://')
            if not url_pattern.match(link):
                return jsonify({'message': '无效的URL格式。'}), 400

            # Determine platform based on URL
            platform_from_link = determine_platform(link)
            print(platform_from_link,platform)
            if not platform_from_link:
                return jsonify({'message': '不支持的平台。'}), 400

            # Check if platform matches
            if platform_from_link != platform:
                return jsonify({'message': f'提交的链接平台 ({platform_from_link}) 与选择的平台 ({platform}) 不匹配。'}), 400


            # Check for duplicate link
            if link in submitted_video_links:
                return jsonify({'message': f'{link} 该视频链接已提交过。'}), 400

            # Add link to submitted_video_links
            submitted_video_links[link] = send_id

            # noteMessage = run_spider.run_spider(link, {})
            # print(noteMessage)

            # Collect data to DataFrame
            video_data = {
                '项目': [project_name],
                '负责人': [manager],
                '花费': [cost],
                '产品': [product],
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
            project_name = data.get('项目')
            manager = data.get('负责人')
            cost = data.get('花费')
            product = data.get('产品')
            ProgressCooperation = data.get('合作进度')
            estimatedViews = data.get('预估观看量')
            estimatedLaunchDate = data.get('预估上线时间')

            # 处理空字符串，将其转换为 None
            video_data = {
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
            all_columns = ['id', '平台', '类型', '红人名称', '发布时间', '播放量', '点赞数', '评论数', '收藏数', '转发数', '参与率',
                           '更新日期', '项目', '负责人', '合作进度', '物流进度', '物流单号', '花费', '产品', '预估观看量', '预估上线时间']
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

