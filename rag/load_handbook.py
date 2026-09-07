import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""把 data/employee_handbook.txt 切块后存入 MySQL 的 documents + chunks 表"""
import mysql.connector
from db_config import DB_CONFIG
from splitter import split_text  # 复用第 3 课的切分函数

def main():
    # 1. 读员工手册
    with open("data/employee_handbook.txt", encoding="utf-8") as f:
        content = f.read()
    print(f"读取员工手册: {len(content)} 字")

    # 2. 切块
    chunks = split_text(content, chunk_size=300, overlap=50)
    print(f"切成 {len(chunks)} 块")

    # 3. 连 MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 4. 在 documents 表建一条记录（员工手册）
    cursor.execute(
        "INSERT INTO documents (user_id, title, status) VALUES (%s, %s, %s)",
        (1, "员工手册-完整版", "ready"),
    )
    doc_id = cursor.lastrowid
    print(f"documents 表新增: id={doc_id}")

    # 5. 每块插入 chunks 表
    for i, chunk in enumerate(chunks, start=1):
        cursor.execute(
            "INSERT INTO chunks (document_id, chunk_index, content) VALUES (%s, %s, %s)",
            (doc_id, i, chunk),
        )
    conn.commit()
    print(f"chunks 表新增 {len(chunks)} 条")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()