"""问答：输入问题 → 检索最相关 chunks → DeepSeek 基于资料回答"""
import sys
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
import os

# DeepSeek API key 从环境变量读（.env 方案，W2 学过）
from dotenv import load_dotenv
load_dotenv()

def main():
    # 1. 取问题（命令行参数）
    question = sys.argv[1] if len(sys.argv) > 1 else "公司请假流程是什么？"
    print(f"问题: {question}")

    # 2. 加载模型 + 向量库
    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="kb_docs")

    # 3. 问题向量化
    q_emb = model.encode([question]).tolist()

    # 4. 检索 Top-3
    results = collection.query(query_embeddings=q_emb, n_results=3)
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    print("\n=== 检索到的 3 个相关片段 ===")
    for i, (doc, meta) in enumerate(zip(docs, metas), 1):
        print(f"[片段{i}] (文档ID={meta['document_id']}, {meta['title']})")
        print(f"  {doc[:80]}...")   # 只显示前80字

    # 5. 拼 prompt
    context = "\n\n".join(docs)
    prompt = f"""你是一个企业知识库助手。请只根据下面提供的资料回答用户问题。
要求：
1. 如果资料中有答案，请基于资料回答，并在末尾注明依据（用资料原文的关键句）。
2. 如果资料中没有答案，请直接回答"资料中未找到相关信息"，绝对不要编造。

资料：
{context}

用户问题：{question}
"""

    # 6. 调用 DeepSeek
    llm = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com"
    )
    resp = llm.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,        # 问答用低温度，减少幻觉
    )
    answer = resp.choices[0].message.content

    print("\n=== 回答 ===")
    print(answer)

if __name__ == "__main__":
    main()