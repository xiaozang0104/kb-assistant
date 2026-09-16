"""数据层：所有数据库操作集中在这里"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="kb_app",
        password=os.environ.get("KB_DB_PASSWORD", ""),
        database="kb_assistant",
        charset="utf8mb4",
    )

def list_users():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, created_at FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def list_documents():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, user_id, title, status, created_at FROM documents")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_document(doc_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def create_document(user_id, title, status="processing"):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, title, status) VALUES (%s, %s, %s)",
        (user_id, title, status),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

def delete_document(doc_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    conn.commit()
    cursor.close()
    conn.close()