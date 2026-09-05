from fastapi import FastAPI
import mysql.connector
from db_config import DB_CONFIG
from pydantic import BaseModel
app = FastAPI()

# 连接数据库（每次请求连一次，简单直观）
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

# 接口1：看所有用户
@app.get("/users")
def list_users():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)  # dictionary=True 让每行变成 dict（就是 JSON 那样）
    cursor.execute("SELECT id, username, created_at FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

#接口2：查所有文档
@app.get("/documents")
def list_documents():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, user_id, title, status, created_at FROM documents")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# 接口3：查单个文档
@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        return {"error": "document not found"}
    return row

# 接口4：新建文档
class DocumentCreate(BaseModel):
    user_id: int
    title: str
    status: str = "processing"   # 默认值

@app.post("/documents")
def create_document(doc: DocumentCreate):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, title, status) VALUES (%s, %s, %s)",
        (doc.user_id, doc.title, doc.status),
    )
    conn.commit()                 # 插入后必须 commit，否则不生效！
    cursor.close()
    conn.close()
    return {"id": cursor.lastrowid, "message": "created"}

# 接口5：删除文档
@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "deleted"}