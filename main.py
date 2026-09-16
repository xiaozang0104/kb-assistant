from fastapi import FastAPI
from pydantic import BaseModel
import services
from agent.kb_agent import ask_agent  # Agent 逻辑

app = FastAPI()

class DocumentCreate(BaseModel):
    user_id: int
    title: str

class ChatRequest(BaseModel):
    question: str

# ---- 路由：只负责接收请求、调 service、返回结果 ----
@app.get("/users")
def list_users():
    return repository.list_users()   # 或 services 里加个包装

@app.get("/documents")
def list_documents():
    return services.get_all_documents()

@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    doc = repository.get_document(doc_id)
    if doc is None:
        return {"error": "document not found"}
    return doc

@app.post("/documents")
def create_document(doc: DocumentCreate):
    try:
        new_id = services.create_document_with_check(doc.user_id, doc.title)
        return {"id": new_id, "message": "created"}
    except ValueError as e:
        return {"error": str(e)}

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    services.delete_document_safe(doc_id)
    return {"message": "deleted"}

@app.post("/chat")
def chat(req: ChatRequest):
    return ask_agent(req.question)