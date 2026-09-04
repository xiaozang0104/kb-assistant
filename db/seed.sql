INSERT INTO users (username, password_hash) VALUES ('alice', 'fakehash123');
INSERT INTO documents (user_id, title, status) VALUES (1, '员工手册-第一章', 'ready');
INSERT INTO documents (user_id, title, status) VALUES (1, '员工手册-第二章', 'processing');

INSERT INTO users (username, password_hash) VALUES ('bob', 'fakehash456');
INSERT INTO documents (user_id, title, status) VALUES (2, '员工手册-第三章', 'ready');

INSERT INTO chunks (document_id, chunk_index, content) VALUES (1, 1, '第一章第一小节');
INSERT INTO chunks (document_id, chunk_index, content) VALUES (1, 2, '第一章第二小节');
INSERT INTO chunks (document_id, chunk_index, content) VALUES (1, 3, '第一章第三小节');

INSERT INTO chunks (document_id, chunk_index, content) VALUES (2, 1, '第二章第一小节');
INSERT INTO chunks (document_id, chunk_index, content) VALUES (2, 2, '第二章第二小节');
INSERT INTO chunks (document_id, chunk_index, content) VALUES (2, 3, '第二章第三小节');

INSERT INTO chunks (document_id, chunk_index, content) VALUES (3, 1, '第三章第一小节');
INSERT INTO chunks (document_id, chunk_index, content) VALUES (3, 2, '第三章第二小节');
INSERT INTO chunks (document_id, chunk_index, content) VALUES (3, 3, '第三章第三小节');

INSERT INTO conversations (user_id, title) VALUES (1, '新会话');

INSERT INTO messages (conversation_id, role, content) VALUES (1, 'user','你好！');
INSERT INTO messages (conversation_id, role, content) VALUES (1, 'assistant','你好！');
INSERT INTO messages (conversation_id, role, content) VALUES (1, 'user','你叫什么？');
INSERT INTO messages (conversation_id, role, content) VALUES (1, 'assistant','我叫小爱。');