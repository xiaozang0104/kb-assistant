"""业务层：业务逻辑（校验、规则），不直接写 SQL"""
import repository

def get_all_documents():
    """获取所有文档（简单透传，以后可加权限过滤等规则）"""
    return repository.list_documents()

def create_document_with_check(user_id, title):
    """新建文档前检查：用户必须存在"""
    users = repository.list_users()
    user_ids = [u["id"] for u in users]
    if user_id not in user_ids:
        raise ValueError(f"用户 {user_id} 不存在")
    return repository.create_document(user_id, title)

def delete_document_safe(doc_id):
    """删除文档：先删它的 chunks（子表），再删文档本身（外键约束）"""
    # W4 讲过：chunks 外键指向 documents，先删子表
    conn = repository.get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chunks WHERE document_id = %s", (doc_id,))
    cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    conn.commit()
    cursor.close()
    conn.close()