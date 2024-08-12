import datetime

import pandas as pd
from flask import Blueprint, request, jsonify, current_app

from base import DF_ToSql
from base import DatabaseUpdater
from base import ReadDatabase
from forms import ProjectForm
from utils import sanitize_input

project_information_bp = Blueprint('project_information', __name__)

class ProjectInformation:
    @staticmethod
    @project_information_bp.route('/get_projects', methods=['GET'])
    def get_projects():
        try:
            DATABASE = 'marketing'
            sql = 'SELECT DISTINCT 项目 FROM influencers_project_info'
            current_app.logger.info(f"执行SQL查询: {sql}")
            projects_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {projects_df}")
            projects = projects_df['项目'].tolist()
            return jsonify({'projects': projects}), 200
        except Exception as e:
            current_app.logger.error(f"获取项目信息失败: {e}")
            return jsonify({'message': f'获取项目信息失败: {e}'}), 500

    @staticmethod
    @project_information_bp.route('/get_managers', methods=['GET'])
    def get_managers():
        try:
            DATABASE = 'marketing'
            sql = 'SELECT DISTINCT 负责人 FROM influencers_project_info'
            current_app.logger.info(f"执行SQL查询: {sql}")
            managers_df = ReadDatabase(DATABASE, sql).vm()
            current_app.logger.info(f"查询结果: {managers_df}")
            managers = managers_df['负责人'].tolist()
            return jsonify({'managers': managers}), 200
        except Exception as e:
            current_app.logger.error(f"获取负责人信息失败: {e}")
            return jsonify({'message': f'获取负责人信息失败: {e}'}), 500



    @staticmethod
    @project_information_bp.route('/submit', methods=['POST'])
    def submit():
        try:
            data = request.json
            form = ProjectForm(data=data)

            if form.validate():
                project_name = sanitize_input(data.get('projectName'))
                manager = sanitize_input(data.get('manager'))
                progress = sanitize_input(data.get('progress'))
                cost = data.get('cost')
                product = sanitize_input(data.get('product'))
                estimated_views = data.get('estimatedViews')
                estimated_launch_date = data.get('estimatedLaunchDate')

                # 记录操作
                current_app.logger.info(f"提交项目: {project_name}, 负责人: {manager}")
                print(f"项目: {project_name}, 负责人: {manager}, 合作进度: {progress}, 花费: {cost}, 产品: {product}, 预估观看量: {estimated_views}, 预估上线时间: {estimated_launch_date}")

                # 将数据收集到一个字典中
                project_data = {
                    '项目': [project_name],
                    '负责人': [manager],
                    '合作进度': [progress],
                    '花费': [cost],
                    '产品': [product],
                    '预估观看量': [estimated_views],
                    '预估上线时间': [estimated_launch_date],
                }
                update_date = datetime.date.today()
                project_data['更新日期'] = update_date
                df = pd.DataFrame(project_data)

                # 定义索引字段
                index_fields = ['项目', '负责人', '花费', '产品']

                # 检查表是否存在
                DATABASE = 'marketing'
                sql_t = 'influencers_project_info'
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
                    index_exists = False
                    try:
                        index_info = ReadDatabase(DATABASE, f"SHOW INDEX FROM {sql_t}").vm()
                        index_columns = index_info[index_info['Key_name'] == 'PRIMARY']['Column_name'].tolist()
                        index_exists = set(index_fields).issubset(set(index_columns))
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
            else:
                return jsonify({'message': '输入验证失败。'}), 400

        except Exception as e:
            current_app.logger.error(f"内部服务器错误: {e}")
            return jsonify({'message': '内部服务器错误。'}), 500

