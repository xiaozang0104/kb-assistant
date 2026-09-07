from fastapi import FastAPI
import mysql.connector
from db_config import DB_CONFIG
from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()   # 读 .env（如果 db_config.py 里已经 load 过，这里可以省略，但保险加上）
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
app = FastAPI()
# RAG 组件：全局加载一次（模型加载很慢，不能放接口函数里每次加载）
print("加载 RAG 模型...（首次约 5~10 秒）")
rag_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
kb_collection = chroma_client.get_or_create_collection(name="kb_docs")
print("RAG 模型加载完成")

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

from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(req: AskRequest):
    """RAG 问答接口：检索 + 生成"""
    # 1. 问题向量化
    q_emb = rag_model.encode([req.question]).tolist()

    # 2. 检索 Top-3
    results = kb_collection.query(query_embeddings=q_emb, n_results=3)
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # 3. 拼 prompt
    context = "\n\n".join(docs)
    prompt = f"""你是企业知识库助手。只根据资料回答，资料没有就回答"资料中未找到相关信息"，不要编造。

资料：
{context}

问题：{req.question}"""

    # 4. 调用 DeepSeek
    llm = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com"
    )
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    # 5. 返回回答 + 引用来源（溯源！）
    return {
        "answer": resp.choices[0].message.content,
        "sources": [
            {"document_id": m["document_id"], "title": m["title"], "snippet": d[:100]}
            for d, m in zip(docs, metas)
        ],
    }