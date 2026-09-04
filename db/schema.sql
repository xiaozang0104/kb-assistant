-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- 主键，自增
    username VARCHAR(50) NOT NULL UNIQUE,     -- 用户名：必填、唯一
    password_hash VARCHAR(255) NOT NULL,      -- 密码哈希
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP  -- 创建时间，默认当前
);

-- 文档表（示范外键写法）
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'processing',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)   -- 外键：指向 users.id
);

CREATE TABLE chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id)   -- 外键：指向 documents.id
);

CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间，默认当前
    FOREIGN KEY (user_id) REFERENCES users(id)  -- 外键
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 创建时间，默认当前
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)   -- 外键
);