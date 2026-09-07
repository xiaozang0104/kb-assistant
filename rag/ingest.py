import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""入库：从 MySQL 的 chunks 表读取内容，向量化后存入 Chroma"""
import mysql.connector
from sentence_transformers import SentenceTransformer
import chromadb
from db_config import DB_CONFIG

def main():
    # 1. 加载 embedding 模型（首次会加载缓存，几秒钟）
    print("加载 embedding 模型...")
    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

    # 2. 从 MySQL 读所有 ready 文档的 chunks
    print("从 MySQL 读取 chunks...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id AS chunk_id, c.content, d.id AS document_id, d.title
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE d.status = 'ready'
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    print(f"读到 {len(rows)} 个 chunk")

    if not rows:
        print("没有可入库的内容，请先运行 load_handbook.py")
        return

    # 3. 批量向量化（model.encode 一次处理所有文本，比循环快）
    print("向量化中...")
    texts = [r["content"] for r in rows]
    embeddings = model.encode(texts).tolist()

    # 4. 存入 Chroma
    print("写入 Chroma...")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="kb_docs")

    # 清空旧的（防止重复运行 id 冲突）
    # 清空集合里所有数据（用 id 前缀匹配不可行，直接删集合重建最干净）
    try:
        ids = collection.get()["ids"]
        if ids:
            collection.delete(ids=ids)
    except Exception:
        pass

    collection.add(
        ids=[str(r["chunk_id"]) for r in rows],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"document_id": r["document_id"], "title": r["title"]} for r in rows],
    )
    print(f"入库完成: {len(rows)} 条向量已存入 Chroma")

if __name__ == "__main__":
    main()