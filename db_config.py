import os
from dotenv import load_dotenv

load_dotenv()   # 自动读 .env 文件

DB_CONFIG = {
    "host": "localhost",
    "user": "kb_app",
    "password": os.environ.get("KB_DB_PASSWORD", ""),
    "database": "kb_assistant",
    "charset": "utf8mb4",
}