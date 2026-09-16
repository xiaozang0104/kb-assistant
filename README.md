# kb-assistant

企业知识库智能助手：基于 FastAPI + MySQL + Chroma + DeepSeek 的 RAG 问答与 Agent 系统。
(English description...)

## Features（功能）
- 文档管理 CRUD（REST API）
- RAG 知识库问答（带引用来源）
- AI Agent（Function Calling：知识检索 / 数据库查询 / 计算器）

## Tech Stack（技术栈）
- Backend: FastAPI, Python 3.13
- Database: MySQL 8
- Vector DB: Chroma
- Embedding: BGE-small-zh
- LLM: DeepSeek API

## Quick Start（快速开始）
1. 安装依赖: pip install -r requirements.txt
2. 配置 .env（数据库密码 + API key）
3. 导入数据库: db/schema.sql
4. 入库文档: python rag/load_handbook.py
5. 启动: uvicorn main:app --reload

## API
| Method | Path | Description |
|---|---|---|
| GET | /users | list users |
| GET | /documents | list documents |
| POST | /documents | create document |
| DELETE | /documents/{id} | delete document |
| POST | /ask | RAG question answering |
| POST | /chat | Agent chat with tools |

## Architecture
See [System Architecture](docs/system_architecture.md) for the full design.

## Tests
pytest test_splitter.py