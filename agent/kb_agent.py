"""kb_agent.py: 企业知识库智能助手 Agent（检索 + 查库 + 计算）"""
import os
import json
import mysql.connector
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

# ---- 加载 RAG 组件（和 W4 main.py 一样，全局加载一次）----
print("加载模型...")
rag_model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
kb = chroma_client.get_or_create_collection(name="kb_docs")

# ---- 工具声明 ----
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "在员工手册知识库中检索信息。当用户询问公司制度（请假、报销、考勤、年假、加班等）时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "要检索的问题"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_documents_db",
            "description": "查询数据库中的文档统计信息，如某用户上传了多少文档、文档状态等",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "只读 SELECT 查询语句"}
                },
                "required": ["sql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    }
]

# ---- 工具实现 ----
def search_kb(query: str) -> str:
    """工具1：检索员工手册知识库（复用 W4 的 RAG）"""
    q_emb = rag_model.encode([query]).tolist()
    results = kb.query(query_embeddings=q_emb, n_results=3)
    if not results["documents"][0]:
        return "知识库中没有找到相关信息"
    # 返回前 2 个最相关片段（控制 token）
    parts = []
    for doc, meta in zip(results["documents"][0][:2], results["metadatas"][0][:2]):
        parts.append(f"[来自文档{meta['document_id']}] {doc}")
    return "\n".join(parts)


def query_documents_db(sql: str) -> str:
    """工具2：执行只读 SQL 查询（安全：只允许 SELECT）"""
    sql = sql.strip().lower()
    if not sql.startswith("select"):
        return "错误：只允许 SELECT 查询"
    if "insert" in sql or "delete" in sql or "update" in sql or "drop" in sql:
        return "错误：只允许 SELECT 查询"
    try:
        conn = mysql.connector.connect(**get_db_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if not rows:
            return "查询结果为空"
        # 只返回前 5 行，转成易读文本
        return json.dumps(rows[:5], ensure_ascii=False, default=str)
    except Exception as e:
        return f"数据库错误: {e}"


def get_db_config():
    """从环境变量读数据库配置"""
    return {
        "host": "localhost",
        "user": "kb_app",
        "password": os.environ.get("KB_DB_PASSWORD", ""),
        "database": "kb_assistant",
        "charset": "utf8mb4",
    }


def calculator(expression: str) -> str:
    """工具3：计算器（白名单防注入）"""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "错误：非法字符"
    try:
        return f"计算结果: {eval(expression)}"
    except Exception as e:
        return f"计算错误: {e}"


# 工具注册表
TOOL_FUNCTIONS = {
    "search_kb": search_kb,
    "query_documents_db": query_documents_db,
    "calculator": calculator,
}

def ask_agent(question: str, client=None) -> dict:
    """对外提供 Agent 问答：输入问题，返回回答（可能经过多轮工具调用）"""
    if client is None:
        client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
            base_url="https://api.deepseek.com"
        )

    messages = [{"role": "user", "content": question}]
    tool_calls_log = []  # 记录调用了哪些工具（调试/展示用）

    for round_num in range(6):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
        )
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                tool_calls_log.append({"tool": name, "args": args})
                result = TOOL_FUNCTIONS[name](**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
            continue
        else:
            return {"answer": msg.content, "tool_calls": tool_calls_log}

    return {"answer": "任务可能未完成（超过最大轮数）", "tool_calls": tool_calls_log}

def main():
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url="https://api.deepseek.com"
    )

    print("=== 企业知识库智能助手 Agent ===")
    print("输入问题，输入 exit 退出")
    print("试试：公司请假流程？/ 数据库里有多少个文档？/ alice 有几个文档？文档平均多少chunk？")

    while True:
        question = input("\n你: ")
        if question.lower() == "exit":
            break

        result = ask_agent(question, client=client)
        print(f"\n[Agent] {result['answer']}")

if __name__ == "__main__":
    main()