-- 问：alice 上传了哪些文档？
SELECT id, title, status FROM documents WHERE user_id = 1;

-- 问：会话 1 里每句话是谁说的（用户还是 AI）？
SELECT m.id, m.role, m.content
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.id = 1;

-- 问：每个用户各传了多少文档？
SELECT user_id, COUNT(*) AS doc_count
FROM documents
GROUP BY user_id;

-- 问：谁传的文档最多？
SELECT username FROM users
WHERE id = (
    SELECT user_id FROM documents
    GROUP BY user_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
);

-- 把文档 2 的状态从 processing 改成 ready
UPDATE documents SET status = 'ready' WHERE id = 2;

-- 删除一个测试会话：必须先删它的消息，再删会话本身！
DELETE FROM messages WHERE conversation_id = 1;
DELETE FROM conversations WHERE id = 1;