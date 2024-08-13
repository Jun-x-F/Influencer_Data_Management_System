from flask import Blueprint, request, jsonify, current_app
from utils import sanitize_input
from base import ReadDatabase, DF_ToSql, DatabaseUpdater
import pandas as pd
import datetime
from sqlalchemy import text
pd.set_option('display.max_columns', None)
update_bp = Blueprint('update', __name__)

class UpdateInfluencer:
    @staticmethod
    @update_bp.route('/get_platforms', methods=['GET'])
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
    @update_bp.route('/get_influencers', methods=['POST'])
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
    @update_bp.route('/influencer', methods=['POST'])
    def update_influencer():
        try:
            data = request.json
            platform = sanitize_input(data.get('platform'))
            name = sanitize_input(data.get('name'))
            email = sanitize_input(data.get('email'))
            whatsapp = sanitize_input(data.get('whatsapp'))
            discord = sanitize_input(data.get('discord'))
            address1 = sanitize_input(data.get('address1'))
            address2 = sanitize_input(data.get('address2'))
            address3 = sanitize_input(data.get('address3'))
            tag1 = sanitize_input(data.get('tag1'))
            tag2 = sanitize_input(data.get('tag2'))
            tag3 = sanitize_input(data.get('tag3'))
            country = sanitize_input(data.get('country'))
            country_code = sanitize_input(data.get('country_code'))

            if not platform or not name:
                return jsonify({'message': '平台和红人名称是必需的。'}), 400
            update_date = datetime.date.today()
            influencer_data = {
                '平台': [platform],
                '红人名称': [name],
                '邮箱': [email],
                'WhatsApp': [whatsapp],
                'Discord': [discord],
                '地址信息1': [address1],
                '地址信息2': [address2],
                '地址信息3': [address3],
                '标签功能1': [tag1],
                '标签功能2': [tag2],
                '标签功能3': [tag3],
                '国家': [country],
                '国家编码': [country_code],
                '更新日期': [update_date]
            }

            update_date = datetime.date.today()
            influencer_data['更新日期'] = update_date
            df = pd.DataFrame(influencer_data)
            # 删除空列
            df.replace('', pd.NA, inplace=True)
            df = df.dropna(axis=1, how='all')
            # print(df)

            # 定义索引字段
            index_fields = ['平台','红人名称']

            # 检查表是否存在
            DATABASE = 'marketing'
            sql_t = 'celebrity_profile'
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
    @update_bp.route('/get_influencer_data', methods=['GET'])
    def get_influencer_data():
        DATABASE = 'marketing'
        sql_t = 'celebrity_profile'
        try:
            data = ReadDatabase(DATABASE, f'SELECT * FROM {sql_t}').vm()  # 假设 ReadDatabase 函数返回的是 DataFrame
            # 处理空值和特殊值
            # 处理 NaN 和 inf 值
            data = data.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
            data = data.fillna('')
            result = data.to_dict(orient='records')  # 将 DataFrame 转换为字典列表
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500



