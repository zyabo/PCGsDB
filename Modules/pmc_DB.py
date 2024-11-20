import pandas as pd
import sqlite3

def pmc_csv2DB(dir_paths):
    # Step 1: 读取CSV文件
    csv_file = dir_paths["PMC-Patients.csv"]  # 将这里的路径替换为你的CSV文件路径
    df = pd.read_csv(csv_file)

    # Step 2: 连接到SQLite数据库
    db_file = dir_paths["PMC-Patients.db"]  # 将这里的路径替换为你的SQLite数据库文件路径
    conn = sqlite3.connect(db_file)

    # Step 3: 将数据写入数据库
    df.to_sql('table_name', conn, if_exists='replace', index=False)  # 'table_name' 替换为你希望创建的表名

    # Step 4: 关闭数据库连接
    conn.close()


def pmc_searchDB(dir_paths):
    # Step 1: 连接到SQLite数据库
    db_file = dir_paths["PMC-Patients.db"]  # 将这里的路径替换为你的SQLite数据库文件路径
    conn = sqlite3.connect(db_file)

    # 创建一个Cursor对象并执行SQL查询
    cursor = conn.cursor()
    query = """
    SELECT *
    FROM table_name
    WHERE patient LIKE '%Breast%' AND patient LIKE '%BRCA1%'
    """
    cursor.execute(query)

    # 获取查询结果
    results = cursor.fetchall()

    # 打印结果
    for row in results:
        print(row)

    # 关闭数据库连接
    conn.close()

import os
def check_DB(dir_paths):
    # PMC-Patients
    check_pass_DB = True
    if not os.path.exists(dir_paths["PMC-Patients.csv"]):
        print("{} does not exist. Please download the file from {} and then place the file in {}.".format(
            "PMC-Patients.csv", "https://huggingface.co/datasets/zhengyun21/PMC-Patients/blob/main/PMC-Patients.csv",
            dir_paths["PMC-Patients.csv"]))
        check_pass_DB = False

    if not os.path.exists(dir_paths["PMC-Patients.db"]):
        if os.path.exists(dir_paths["PMC-Patients.csv"]):
            pmc_csv2DB(dir_paths)
        else:
            check_pass_DB = False

    if not os.path.exists(dir_paths["disgenet_2020.db"]):
        print("{} does not exist. Please download the file and then place the file in {}."
              .format("disgenet_2020.db", dir_paths["disgenet_2020.db"]))
        check_pass_DB = False

    if not os.path.exists(dir_paths["Census_abbreviations.csv"]):
        print("{} does not exist. Please download the file and then place the file in {}."
              .format("Census_abbreviations.csv", dir_paths["Census_abbreviations.csv"]))
        check_pass_DB = False

    if not os.path.exists(dir_paths["Census_allTue May 14 09_10_51 2024.csv"]):
        print("{} does not exist. Please download the file and then place the file in {}."
              .format("Census_allTue May 14 09_10_51 2024.csv", dir_paths["Census_allTue May 14 09_10_51 2024.csv"]))
        check_pass_DB = False
    return check_pass_DB