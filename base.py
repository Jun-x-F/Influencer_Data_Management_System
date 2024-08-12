# # -*- coding: utf-8 -*-
# @Time : 2023/3/1 14:55
# @Author : DELL
# @Email : wayne_lau@aliyun.com
# @File : base.py
# @Project : share_class


import pandas as pd
from sqlalchemy import DATE
from sqlalchemy import String, BigInteger, Float, Boolean, SmallInteger, Integer, DateTime, Interval, text, Text
from sqlalchemy.connectors import pyodbc
from sqlalchemy.types import NVARCHAR

# 共享的数据库主机配置
SHARED_DB_CONFIG = {
    'vm2': {
        'driver': 'mysql+pymysql',
        'user': 'user1',
        'password': 'MisAdmin123#.',
        'host': '120.79.205.19',
        'port': '3306',
        'charset': 'utf8'
    },
    'host_163': {
        'driver': 'mysql+pymysql',
        'user': 'user1',
        'password': 'user1',
        'host': '172.16.11.163',
        'port': '3306',
        'charset': 'utf8mb4'
    },
'vm': {
        'driver': 'mysql+pymysql',
        'user': 'user1',
        'password': 'user1',
        'host': '172.16.11.163',
        'port': '3306',
        'charset': 'utf8mb4'
    },
    'host_229': {
        'driver': 'mysql+pymysql',
        'user': 'jisu',
        'password': 'jisulife',
        'host': '172.16.11.229',
        'port': '3306',
        'charset': 'utf8mb4'
    },
    'host_236': {
        'driver': 'mysql+pymysql',
        'user': 'root',
        'password': '123456',
        'host': '172.16.11.236',
        'port': '3306',
        'charset': 'utf8mb4'
    },
    'host_236_mssql': {
        'driver': 'mssql+pymssql',
        'user': 'sa',
        'password': 'sql123.',
        'host': '172.16.11.236',
        'port': '3306'
    }
}

# 特定的数据库配置
DB_CONFIG = {
    # 阿里云
    'information_schema': {**SHARED_DB_CONFIG['vm2'], 'db': 'information_schema'},
    'lingxing': {**SHARED_DB_CONFIG['vm2'], 'db': 'lingxing'},
    'lx_kingdee': {**SHARED_DB_CONFIG['vm2'], 'db': 'lx_kingdee'},
    'mysql': {**SHARED_DB_CONFIG['vm2'], 'db': 'mysql'},
    'performance_schema': {**SHARED_DB_CONFIG['vm2'], 'db': 'performance_schema'},

    # 163
    'kingdee': {**SHARED_DB_CONFIG['host_163'], 'db': 'kingdee'},
    'amazon': {**SHARED_DB_CONFIG['host_163'], 'db': 'amazon'},
    'amazon_new': {**SHARED_DB_CONFIG['host_163'], 'db': 'amazon_new'},
    'shopify': {**SHARED_DB_CONFIG['host_163'], 'db': 'shopify'},
    'shopify_new': {**SHARED_DB_CONFIG['host_163'], 'db': 'shopify_new'},
    'wps': {**SHARED_DB_CONFIG['host_163'], 'db': 'wps'},
    'platform': {**SHARED_DB_CONFIG['host_163'], 'db': 'platform'},
    'powerbi_data': {**SHARED_DB_CONFIG['host_163'], 'db': 'powerbi_data'},
    'dataops_monitor': {**SHARED_DB_CONFIG['host_163'], 'db': 'dataops_monitor'},
    'marketing': {**SHARED_DB_CONFIG['host_163'], 'db': 'marketing'},

    # 229
    'jsaux_service_db': {**SHARED_DB_CONFIG['host_229'], 'db': 'jsaux_service_db'},

    # 236
    'service_db': {**SHARED_DB_CONFIG['host_236'], 'db': 'service_db'},
    'jsaux_data': {**SHARED_DB_CONFIG['host_236_mssql'], 'db': 'jsaux_data'}
}

def create_engine_for_db(database_t):
    """
    根据数据库类型创建数据库连接

    :param database_t: 数据库类型
    :return: 数据库连接引擎
    """
    if database_t not in DB_CONFIG:
        raise ValueError("没有这个数据库")

    config = DB_CONFIG[database_t]
    connection_string = f"{config['driver']}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db']}?charset={config['charset']}"
    return sqlalchemy.create_engine(connection_string)

class DF_ToSql(object):
    def __init__(self, datas, database_t, sqltable_name, tosql_if_exists,dtypedict=None):
        self.datas = datas                                  # 传入的 DataFrame
        self.database_t = database_t                        # 数据库类型
        self.sqltable_name = sqltable_name                  # SQL 表名
        self.tosql_if_exists = tosql_if_exists              # to_sql 插入数据库的方式
        self.engine = create_engine_for_db(database_t)  # 初始化数据库引擎
        self.dtypedict = dtypedict

    def mapping_df_types(self):
        datas_df = pd.DataFrame(self.datas)
        # 确保所有id的数据类型为bigint
        id_columns = [col for col in datas_df.columns if 'id' in col.lower()]
        # print('id_columns', id_columns)

        if self.dtypedict is None:
            self.dtypedict = {}

        # 对包含'id'的列进行处理
        for col in id_columns:
            if col not in self.dtypedict:
                # 对未在dtypedict中指定类型的列进行处理
                if col == 'order-id':
                    # 如果列名为'order-id'，转换为字符串
                    datas_df[col] = datas_df[col].astype(str)
                else:
                    # 否则，转换为Pandas的Int64类型
                    try:
                        datas_df[col] = datas_df[col].astype('Int64')
                    except ValueError as e:
                        print(f"Error converting column {col}: {e}")
        pandas_to_sqlalchemy_types = {
            'string': String,
            'int64': BigInteger(),
            'Int64': BigInteger(),
            'float64': Float(precision=2, asdecimal=True),
            'Float64': Float(precision=2, asdecimal=True),
            'boolean': Boolean(),
            'object': String,
            'int8': SmallInteger(),
            'int16': SmallInteger(),
            'int32': Integer(),
            'uint8': SmallInteger(),
            'uint16': Integer(),
            'uint32': BigInteger(),
            'uint64': BigInteger(),
            'float16': Float(precision=2, asdecimal=True),
            'float32': Float(precision=2, asdecimal=True),
            'datetime64': DateTime,
            'timedelta64': Interval(),
            'datetime64[ns]': DateTime,
            'category': String,
            'datetime64[ns, Asia/Shanghai]': DateTime,
        }

        text_type_threshold = 255  # 设置转换为 TEXT 的阈值
        safety_margin = 50  # 设置安全边距
        long_text_columns = {'订单项_title', '订单状态url', '订单项_名称','备注','登陆页面网站'}  # 长文本列集合

        dtypedict = self.dtypedict.copy()

        for column in datas_df.columns:
            if "date" in column.lower() or "time" in column.lower():
                dtypedict[column] = DateTime
            else:
                pandas_type = str(datas_df.dtypes[column])
                if pandas_type == 'string' or pandas_type == 'object':
                    max_length = datas_df[column].astype(str).str.len().max()
                    if pd.isna(max_length) or max_length <= text_type_threshold:
                        dtypedict[column] = String(length=int(max_length + safety_margin)) if column not in long_text_columns else Text
                    else:
                        dtypedict[column] = Text
                elif pandas_type in pandas_to_sqlalchemy_types:
                    dtypedict[column] = pandas_to_sqlalchemy_types[pandas_type]
                else:
                    dtypedict[column] = String(length=text_type_threshold)  # 对于未知类型，默认为字符串类型
        # 创建数据库引擎
        engine = create_engine_for_db(self.database_t)

        # 数据导入 SQL
        datas_df.to_sql(self.sqltable_name, con=engine, chunksize=10000, if_exists=self.tosql_if_exists, index=False, dtype=dtypedict)
        print(f'{self.database_t}数据库的 {self.sqltable_name} 表插入成功')
        return self

    def index_exists(self, table_name, index_name):
        """
        检查给定表上是否已经存在指定的索引。

        :param table_name: 表名
        :param index_name: 索引名
        :return: 布尔值，表示索引是否存在
        """
        query = text(
            "SELECT COUNT(*) FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() AND "
            "table_name = :table AND index_name = :index"
        )
        with self.engine.connect() as conn:
            result = conn.execute(query, {'table': table_name, 'index': index_name}).scalar()
            return result > 0

    def add_index(self, columns, index_name=None, index_type=None):
        """
        在数据库表上添加索引，如果索引不存在。如果to_sql时选择的是append也不影响 会输出索引已存在

        :param columns: 索引列， 列表格式。注意要加中括号 比如：['MSKU']、['MSKU','统计日期']
        :param index_name: 索引名，如果为 None，则自动生成（按列名，比如MSKU则为MSKU_idx）
        :param index_type: 索引类型，如 'UNIQUE', 'FULLTEXT',如果为 None，则为普通索引
        """
        # 自动生成索引名（如果没有提供）
        if index_name is None:
            # 使用列名生成索引名
            columns_str = '_'.join(columns)
            index_name = f"{columns_str}_idx"

            if index_type:
                index_name = f"{index_type.lower()}_{index_name}"

        if not self.index_exists(self.sqltable_name, index_name):
            columns_str = ', '.join(columns)
            index_type_str = f"{index_type} " if index_type else ""
            create_index_sql = f"ALTER TABLE {self.sqltable_name} ADD {index_type_str}INDEX {index_name} ({columns_str});"
            with self.engine.connect() as conn:
                conn.execute(text(create_index_sql))
            print(f"Index {index_name} ({index_type_str.strip()}) added to {self.sqltable_name} on columns {columns_str}")
        else:
            print(f"索引 {index_name} 已经存在于表 {self.sqltable_name}")
        return self


class ReadDatabase(object):
    def __init__(self,database,sqlcmd):
        self.database = database
        self.sqlcmd = sqlcmd

    def create_engine(self, host, user, password, port):
        db_uri = f'mysql+pymysql://{user}:{password}@{host}:{port}/{self.database}?charset=utf8'
        return create_engine(db_uri)
    def vm(self):
        engine = self.create_engine('172.16.11.163', 'user1', 'user1', 3306)
        df = pd.read_sql(self.sqlcmd, con=engine)
        return df

    def vm2(self):
        engine = self.create_engine('120.79.205.19', 'user1', 'MisAdmin123#.', 3306)
        df = pd.read_sql(self.sqlcmd, con=engine)
        return df

    def dell(self):
        engine = self.create_engine('172.16.11.236', 'root', '123456', 3306)
        df = pd.read_sql(self.sqlcmd, con=engine)
        return df

    def jsaux(self):
        engine = self.create_engine('172.16.11.229', 'jisu', 'jisulife', 3306)
        df = pd.read_sql(self.sqlcmd, con=engine)
        return df


    def sqlserver(self):
        server = "172.16.11.236"
        database = self.database
        username = "sa"
        password = "sql123."
        # 创建连接字符串
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        # 连接到SQL Server
        connection = pyodbc.connect(connection_string)

        # 使用连接执行查询并将结果转换为DataFrame
        query = self.sqlcmd
        df = pd.read_sql_query(query, connection)
        return df

# sql server 使用
class sheet_insert_sql():
# 保存到云文档
    def sku_material_to_yun(self,database_type,file_name,sheetname,sql_t,tosql_if_exists,datetype,dtypedict1=None,col_list = None):
        datas = pd.read_excel(file_name,sheet_name=sheetname)
        datas = pd.DataFrame(datas,columns=col_list)
        # datas.columns = [x.strip() for x in datas.columns]
        print(datas)

        dtypedict = {}
        for i, j in zip(datas.columns, datas.dtypes):
            if i in datetype and datetype != '':
                dtypedict.update({i: DATE})
            elif "object" in str(j):
                dtypedict.update({i: NVARCHAR(length=255)})
            elif "float" in str(j):
                dtypedict.update({i: Float(precision=2, asdecimal=True)})
            elif "int" in str(j):
                dtypedict.update({i: BigInteger()})
        print('dtypedict', dtypedict)

        if database_type == 'mysql':
            if file_name == 'C:/Users/DELL/Documents/WPSDrive/518675718\WPS云盘/JSAUX工作文档11/JSAUX每日出货表.xlsx':
                print('dtypedict1', dtypedict1)
                con2_ = sqlalchemy.create_engine(
                    'mysql+pymysql://jisu:jisulife@172.16.11.229/jsaux_service_db?charset=utf8')
                datas.to_sql(sql_t, con=con2_, chunksize=10000, if_exists=tosql_if_exists,
                             index=False, dtype=dtypedict)  # if_exists = fail 表不存在就创建表 replace
                print('sql插入成功')
            else:
                con2_ = sqlalchemy.create_engine('mysql+pymysql://jisu:jisulife@172.16.11.229/jsaux_service_db?charset=utf8')
                datas.to_sql(sql_t, con=con2_, chunksize=10000, if_exists=tosql_if_exists,
                             index=False,dtype=dtypedict)  # if_exists = fail 表不存在就创建表 replace
                print('sql插入成功')
        elif database_type == 'sqlserver':
            con2_ = sqlalchemy.create_engine("mssql+pymssql://sa:sql123.@localhost:1433/jsaux_data")
            datas.to_sql(sql_t, con=con2_, chunksize=10000, if_exists=tosql_if_exists,
                         index=False,dtype=dtypedict)  # if_exists = fail 表不存在就创建表 replace
            print('sql插入成功')

        else:
            con2_ = sqlalchemy.create_engine(
                'mysql+pymysql://jisu:jisulife@172.16.11.229/jsaux_service_db?charset=utf8')
            datas.to_sql(sql_t, con=con2_, chunksize=10000, if_exists=tosql_if_exists,
                         index=False,dtype=dtypedict)  # if_exists = fail 表不存在就创建表 replace
            print('sql插入成功')


from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import datetime


class DatabaseUpdater:
    def __init__(self):
        """
        初始化方法，在此直接配置每个数据库的连接。
        根据需要配置不同的数据库连接。
        """
        # 配置数据库连接
        # 注意：这里的连接字符串需要根据实际情况进行更改
        self.vm_kingdee = create_engine('mysql+pymysql://user1:user1@172.16.11.163:3306/kingdee?charset=utf8mb4')
        self.vm_amazon = create_engine('mysql+pymysql://user1:user1@172.16.11.163:3306/amazon?charset=utf8mb4')
        self.vm_shopify = create_engine('mysql+pymysql://user1:user1@172.16.11.163:3306/shopify?charset=utf8mb4')
        self.vm_shopify_new = create_engine('mysql+pymysql://user1:user1@172.16.11.163:3306/shopify_new?charset=utf8mb4')
        self.vm_wps = create_engine('mysql+pymysql://user1:user1@172.16.11.163:3306/wps?charset=utf8mb4')
        self.vm_powerbi_data = create_engine('mysql+pymysql://user1:user1@172.16.11.163:3306/powerbi_data?charset=utf8mb4')
        self.vm2_lingxing = create_engine('mysql+pymysql://root:MisAdmin123#.@127.0.0.1:3306/lingxing?charset=utf8mb4')
        self.vm2_lx_kingdee = create_engine('mysql+pymysql://root:MisAdmin123#.@127.0.0.1:3306/lx_kingdee?charset=utf8mb4')
        self.vm_marketing = create_engine('mysql+pymysql://user1:user1@172.16.11.163:3306/marketing?charset=utf8mb4')
        # 可以根据需要添加更多数据库连接

    def get_table_columns(self, engine, table_name):
        """
        获取指定表的所有列名。
        :param engine: SQLAlchemy engine 对象
        :param table_name: 表名
        :return: 表的列名列表
        """
        try:
            query = f"SHOW COLUMNS FROM {table_name};"
            columns_df = pd.read_sql_query(query, engine)
            return columns_df['Field'].tolist()
        except SQLAlchemyError as e:
            print(f"Error getting table columns for {table_name}: {e}")
            return []

    def generate_upsert_statements(self, table_name, df, unique_fields, engine):
        update_statements = []
        table_columns = self.get_table_columns(engine, table_name)
        df_columns = [col for col in df.columns if col in table_columns]  # 保证只使用DataFrame中存在于数据库表中的列

        for index, row in df.iterrows():
            processed_row = row.where(pd.notnull(row), None)
            set_clause_parts = [f"`{col}` = VALUES(`{col}`)" for col in df_columns if col not in unique_fields]
            insert_columns = ', '.join('`' + col + '`' for col in df_columns)
            insert_values = ', '.join(':' + col.replace('-', '_') for col in df_columns)

            set_clause = ', '.join(set_clause_parts)

            update_or_insert_statement = text(f"""
                INSERT INTO {table_name} ({insert_columns})
                VALUES ({insert_values})
                ON DUPLICATE KEY UPDATE {set_clause};
            """)

            params = {col.replace('-', '_'): processed_row[col] for col in df_columns}

            update_statements.append((update_or_insert_statement, params))

        return update_statements

    def update_database_batched(self, engine, table_name, df, unique_fields, batch_size=1000):
        try:
            total_rows = len(df)
            for start_row in range(0, total_rows, batch_size):
                batch_df = df.iloc[start_row:min(start_row + batch_size, total_rows)]
                update_statements = self.generate_upsert_statements(table_name, batch_df, unique_fields, engine)

                with engine.begin() as conn:
                    for statement, params in update_statements:
                        conn.execute(statement, params)

            print(f"Database table {table_name} successfully updated.")
        except SQLAlchemyError as e:
            print(f"Error updating database: {e}")




    def data_monitor(self, task_content=None):

        # 获取监控数据库的数据库名（阿里云的用lx_data_monitor；163的用data_monitor）
        def get_monitor_db(database_t):
            """
            根据当前数据库配置，确定并返回对应的监控数据库名称。
            """
            for config_name, config in DB_CONFIG.items():
                if config['db'] == database_t:
                    if config['host'] == '120.79.205.19':  # 检查键名是否包含 'aliyun'
                        return 'lx_data_monitor'  # 对应阿里云的监控数据库
                    elif config['host'] == '172.16.11.163':  # 检查键名是否包含 'host_163'
                        return 'data_monitor'  # 对应163主机的监控数据库

            # 如果未找到匹配的配置，可以返回一个默认值或抛出异常
            raise ValueError(f"未找到对应的监控数据库配置: {database_t}")

        # 获取数据完整性（返回缺失数据列及数量）
        def calcu_missing_values(df):
            """
            计算DataFrame中每列的缺失值数量，并返回有缺失值的列及其数量的JSON字符串。
            参数:df: 要计算缺失值的pandas DataFrame。
            返回:一个JSON字符串，键为列名，值为该列缺失值的数量，仅包含至少有一个缺失值的列。
            """
            # 计算每列缺失值的数量
            missing_values = df.isna().sum()
            # 过滤出有缺失值的列
            missing_values = missing_values[missing_values > 0]
            # 转换为字典
            missing_values_dict = missing_values.to_dict()
            # 将字典转换为JSON字符串
            missing_values_json = json.dumps(missing_values_dict, ensure_ascii=False)

            return missing_values_json

        # 获取监控数据库的数据库连接
        monitor_engine = create_engine_for_db(get_monitor_db(self.database_t))
        # 创建监控数据库表名（在原表名前加上前缀monitor_）
        monitor_table_name = f"monitor_{self.sqltable_name}"

        # 处理数据量（传入数据的长度）
        updated_rows = len(self.datas)

        # 获取更新时间（当前时间）
        now = pd.Timestamp.now()

        monitor_data = pd.DataFrame({
            'python任务内容': [task_content],
            '数据输入库': [self.database_t],
            '数据输入表': [self.sqltable_name],
            '更新时间': [now],
            '处理数据量': [updated_rows],
            # '数据差异': ['111'],
            '完整性': [calcu_missing_values(self.datas)]
        })

        # 将监控数据插入监控数据库的表中
        monitor_data.to_sql(monitor_table_name, con=monitor_engine, if_exists='append', index=False)

        logging.info(f"Updated {updated_rows} rows in {self.sqltable_name} at {now}.")

        return monitor_data





import sqlalchemy
import json
import logging
from datetime import datetime
import traceback

class DataMonitor:
    def __init__(self, database_t, result_table_name, source_table_name, datas, table_type):
        self.database_t = database_t
        self.result_table_name = result_table_name  # 结果表名，用于存储监控结果
        self.source_table_name = source_table_name  # 数据来源表名
        self.datas = datas  # DataFrame数据
        self.table_type = table_type  # 'fact'或'dimension'


    def calcu_missing_values(self, df):
        """
        计算DataFrame中每列的缺失值数量。
        """
        missing_values = df.isna().sum()
        missing_values = missing_values[missing_values > 0]
        missing_values_dict = missing_values.to_dict()
        return missing_values_dict if missing_values_dict else "No missing values"

    def perform_dimension_monitoring(self, current_data, dimension_columns):
        results = {}
        for column in dimension_columns:
            missing_values_count = current_data[column].isna().sum()
            unique_values_count = current_data[column].nunique()
            duplicate_values_count = current_data[column].duplicated().sum()
            most_frequent_value = current_data[column].mode()[0] if not current_data[column].mode().empty else 'N/A'
            frequency_of_most_frequent = current_data[current_data[column] == most_frequent_value].shape[0] if most_frequent_value != 'N/A' else 0

            results[column] = {
                'missing_count': missing_values_count,
                'unique_count': unique_values_count,
                'duplicate_count': duplicate_values_count,
                'most_frequent_value': most_frequent_value,
                'frequency_of_most_frequent': frequency_of_most_frequent,
            }
        return results

    def perform_fact_monitoring(self, current_data, dimension_columns=None, metric_columns=None):
        # 初始化结果字典，确保每个可能的分析都有默认值
        results = {'度量分析': {}, '维度分析': {}}

        # 指定默认监控结果结构
        default_metric_analysis = {'最大值': 'N/A', '最小值': 'N/A', '平均值': 'N/A'}
        default_dimension_analysis = {'缺失值数量': 'N/A', '重复值数量': 'N/A'}

        # 处理度量列
        metric_columns_to_check = metric_columns if metric_columns else current_data.select_dtypes(include=[np.number]).columns.tolist()
        for column in metric_columns_to_check:
            if pd.api.types.is_numeric_dtype(current_data[column]):
                results['度量分析'][column] = {
                    '最大值': current_data[column].max(),
                    '最小值': current_data[column].min(),
                    '平均值': current_data[column].mean()
                }
            else:
                results['度量分析'][column] = default_metric_analysis

        # 处理维度列
        dimension_columns_to_check = dimension_columns if dimension_columns else current_data.columns.tolist()
        for column in dimension_columns_to_check:
            if column not in metric_columns_to_check:  # 避免重复处理度量列
                results['维度分析'][column] = {
                    '缺失值数量': current_data[column].isna().sum(),
                    '重复值数量': current_data[column].duplicated().sum()
                }
            else:
                results['维度分析'][column] = default_dimension_analysis

        return results

    def data_monitor(self, task_content=None, dimension_columns=None, metric_columns=None):
        start_time = datetime.now()
        try:
            monitor_engine = self.create_engine_for_db(self.database_t)
            monitor_data_list = []

            # 统一处理维度表和事实表监控结果
            monitoring_results = {}
            if self.table_type == 'dimension':
                monitoring_results = self.perform_dimension_monitoring(self.datas, dimension_columns)
                for column, result in monitoring_results.items():
                    data_row = {
                        '列名': column,
                        '缺失值数量': result.get('missing_count', 0),
                        '唯一值数量': result.get('unique_count', 0),
                        '重复值数量': result.get('duplicate_count', 0),
                        '最常见的值': result.get('most_frequent_value', 'N/A'),
                        '最常见值的频次': result.get('frequency_of_most_frequent', 0),
                        '任务内容': task_content,
                        '数据来源表': self.source_table_name,
                        '结果存储表': f"dimension_{self.table_type}_{self.result_table_name}",
                        '开始时间': start_time,
                        '结束时间': datetime.now(),
                        '耗时（秒）': (datetime.now() - start_time).total_seconds(),
                        '处理数据量': len(self.datas),
                    }
                    monitor_data_list.append(data_row)
            elif self.table_type == 'fact':
                monitoring_results = self.perform_fact_monitoring(self.datas, dimension_columns, metric_columns)
                for column, analysis in {**monitoring_results['维度分析'], **monitoring_results['度量分析']}.items():
                    analysis['列名'] = column
                    analysis['任务内容'] = task_content
                    analysis['数据来源表'] = self.source_table_name
                    analysis['结果存储表'] = f"fact_{self.result_table_name}"
                    monitor_data_list.append(analysis)

            monitor_data = pd.DataFrame(monitor_data_list)
            monitor_table_name = f"{self.table_type}_{self.result_table_name}"  # 区分维度表和事实表监控结果的存储表

            # 添加公共信息到DataFrame
            now = pd.Timestamp.now()
            monitor_data['监控时间'] = start_time
            monitor_data['更新时间'] = now
            monitor_data['耗时（秒）'] = (now - start_time).total_seconds()
            monitor_data['处理数据量'] = len(self.datas)

            if not monitor_data.empty:
                monitor_data.to_sql(monitor_table_name, con=monitor_engine, if_exists='replace', index=False)
                logging.info(f"监控结果已成功写入数据库表 {monitor_table_name}。")
            else:
                logging.info("没有数据写入数据库。")
        except Exception as e:
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "stack_trace": traceback.format_exc(),
                "timestamp": datetime.now().isoformat(),
            }
            logging.error(json.dumps(error_info, ensure_ascii=False))

        # return monitor_data  # 或返回错误信息，视需求而定

    def create_engine_for_db(self, database_t):
        # 根据数据库名称创建数据库引擎，这里需要您根据实际情况实现此函数
        # 共享的数据库主机配置
        SHARED_DB_CONFIG = {
            'vm2': {
                'driver': 'mysql+pymysql',
                'user': 'user1',
                'password': 'MisAdmin123#.',
                'host': '120.79.205.19',
                'port': '3306',
                'charset': 'utf8'
            },
            'host_163': {
                'driver': 'mysql+pymysql',
                'user': 'user1',
                'password': 'user1',
                'host': '172.16.11.163',
                'port': '3306',
                'charset': 'utf8mb4'
            },
            'vm': {
                'driver': 'mysql+pymysql',
                'user': 'user1',
                'password': 'user1',
                'host': '172.16.11.163',
                'port': '3306',
                'charset': 'utf8mb4'
            },
            'host_229': {
                'driver': 'mysql+pymysql',
                'user': 'jisu',
                'password': 'jisulife',
                'host': '172.16.11.229',
                'port': '3306',
                'charset': 'utf8mb4'
            },
            'host_236': {
                'driver': 'mysql+pymysql',
                'user': 'root',
                'password': '123456',
                'host': '172.16.11.236',
                'port': '3306',
                'charset': 'utf8mb4'
            },
            'host_236_mssql': {
                'driver': 'mssql+pymssql',
                'user': 'sa',
                'password': 'sql123.',
                'host': '172.16.11.236',
                'port': '3306'
            }
        }

        # 特定的数据库配置
        DB_CONFIG = {
            # 阿里云
            'information_schema': {**SHARED_DB_CONFIG['vm2'], 'db': 'information_schema'},
            'lingxing': {**SHARED_DB_CONFIG['vm2'], 'db': 'lingxing'},
            'lx_kingdee': {**SHARED_DB_CONFIG['vm2'], 'db': 'lx_kingdee'},
            'mysql': {**SHARED_DB_CONFIG['vm2'], 'db': 'mysql'},
            'performance_schema': {**SHARED_DB_CONFIG['vm2'], 'db': 'performance_schema'},

            # 163
            'kingdee': {**SHARED_DB_CONFIG['host_163'], 'db': 'kingdee'},
            'amazon': {**SHARED_DB_CONFIG['host_163'], 'db': 'amazon'},
            'amazon_new': {**SHARED_DB_CONFIG['host_163'], 'db': 'amazon_new'},
            'shopify': {**SHARED_DB_CONFIG['host_163'], 'db': 'shopify'},
            'shopify_new': {**SHARED_DB_CONFIG['host_163'], 'db': 'shopify_new'},
            'wps': {**SHARED_DB_CONFIG['host_163'], 'db': 'wps'},
            'platform': {**SHARED_DB_CONFIG['host_163'], 'db': 'platform'},
            'powerbi_data': {**SHARED_DB_CONFIG['host_163'], 'db': 'powerbi_data'},
            'dataops_monitor': {**SHARED_DB_CONFIG['host_163'], 'db': 'dataops_monitor'},
            'marketing': {**SHARED_DB_CONFIG['host_163'], 'db': 'marketing'},

            # 229
            'jsaux_service_db': {**SHARED_DB_CONFIG['host_229'], 'db': 'jsaux_service_db'},

            # 236
            'service_db': {**SHARED_DB_CONFIG['host_236'], 'db': 'service_db'},
            'jsaux_data': {**SHARED_DB_CONFIG['host_236_mssql'], 'db': 'jsaux_data'}
        }

        if database_t not in DB_CONFIG:
            print(database_t)
            logging.error(f"没有这个数据库: {database_t}")
            raise ValueError(f"没有这个数据库: {database_t}")

        config = DB_CONFIG[database_t]
        connection_string = f"{config['driver']}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db']}?charset={config['charset']}"
        engine = sqlalchemy.create_engine(connection_string)
        return engine

# # 示例使用，需要传递正确的参数
# data_monitor_instance = DataMonitor(database_t='dataops_monitor', sqltable_name='your_table', datas=pd.DataFrame())
# monitor_result = data_monitor_instance.data_monitor(task_content='示例任务内容')
