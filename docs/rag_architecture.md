# RAG Architecture - kb-assistant

> 本图用 Mermaid 绘制，GitHub 会自动渲染。也可在 https://mermaid.live 粘贴预览。

## 系统架构

```mermaid
graph TD
    subgraph 离线入库 Offline
        A[data/employee_handbook.txt<br/>员工手册语料] --> B[rag/load_handbook.py<br/>读取+切块]
        B --> C[(MySQL chunks 表<br/>kb_assistant)]
        C --> D[rag/ingest.py<br/>Embedding 向量化<br/>BGE-small-zh]
        D --> E[(Chroma 向量库<br/>chroma_db/)]
    end

    subgraph 在线问答 Online
        Q[用户问题] --> F[/ask 接口 FastAPI/]
        F --> G[问题 Embedding<br/>BGE-small-zh]
        G --> E
        E --> H[检索 Top-3 相关片段]
        H --> I[拼接 Prompt<br/>资料+问题]
        I --> J[DeepSeek API<br/>deepseek-chat]
        J --> K[回答 + 引用来源 sources]
    end
```

## 流程说明

- **离线入库**（文档上传时执行一次）：员工手册 → 切块存 MySQL chunks 表 → embedding 向量化 → 存 Chroma
- **在线问答**（每次提问执行）：问题向量化 → Chroma 检索最相关 3 块 → 拼 prompt → DeepSeek 生成回答 → 返回回答与引用来源
- 关键文件：`rag/splitter.py`（切块函数）、`rag/load_handbook.py`（入库 MySQL）、`rag/ingest.py`（入库 Chroma）、`rag/query.py`（问答）、`main.py`（/ask 接口）
