"""
简化sql查询方法
@ProjectName: DataAnalysis
@FileName：pandas_sql_models.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/22 上午10:15
"""

from log.logger import LoguruLogger

log = LoguruLogger()

import pandas as pd
from typing import List


@log.log_exceptions
def execute_query(_engine, query: str) -> pd.DataFrame:
    """执行 SQL 查询并返回 DataFrame"""
    return pd.read_sql(query, _engine)
    # with _engine.connect() as connection:
    #     result = connection.execute(text(query))
    #     return pd.DataFrame(result.fetchall(), columns=result.keys())


@log.log_exceptions
def select_data(_engine, _table_name: str, select_clause: str = None,
                where_clause: str = None,
                _group_by: List[str] = None,
                _order_by: List[str] = None) -> pd.DataFrame:
    """模板化 SELECT 查询"""
    _group_by = _group_by or []
    _order_by = _order_by or []

    # 构建 GROUP BY 部分
    group_by_clause = ", ".join(_group_by)
    group_by_clause = f"GROUP BY {group_by_clause}" if _group_by else ""

    # 构建 ORDER BY 部分
    order_by_clause = ", ".join(_order_by)
    order_by_clause = f"ORDER BY {order_by_clause}" if _order_by else ""

    # 组合完整的 SQL 查询
    sql = f"""
        SELECT {select_clause}
        FROM {_table_name}
        {where_clause}
        {group_by_clause}
        {order_by_clause}
    """

    # 执行查询并返回结果
    return execute_query(_engine, sql)

# 示例用法
# if __name__ == "__main__":
#     # 创建数据库引擎
#     engine = create_engine("mysql+pymysql://user:password@host/database")
#
#     # 定义查询条件
#     table_name = "my_table"
#     select_columns = ["column1", "column2"]
#     where_conditions = {"column1": "value1"}
#     group_by = ["column2"]
#     order_by = ["column1 DESC"]
#
#     # 执行查询
#     df = select_data(engine, table_name, select_columns, where_conditions, group_by, order_by)
#     print(df)
