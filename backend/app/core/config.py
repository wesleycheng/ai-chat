"""应用配置"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import json


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "AI Chat Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://aichat:aichat@8.137.103.202:5432/aichat"
    DATABASE_URL_SYNC: str = "postgresql://aichat:aichat@8.137.103.202:5432/aichat"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 加密
    AES_KEY: str = "your-32-byte-aes-key-here!!"  # 必须32字节
    
    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".png", ".jpg", ".jpeg"}
    
    # AI 模型默认配置
    DEFAULT_MAX_TOKENS: int = 4096
    DEFAULT_TEMPERATURE: float = 0.7
    
    # 限流
    RATE_LIMIT_ANONYMOUS: str = "10/minute"
    RATE_LIMIT_AUTHENTICATED: str = "60/minute"
    RATE_LIMIT_CHAT: str = "20/minute"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果 CORS_ORIGINS 是字符串（从环境变量读入的 JSON），解析为列表
        if isinstance(self.CORS_ORIGINS, str):
            try:
                self.CORS_ORIGINS = json.loads(self.CORS_ORIGINS)
            except (json.JSONDecodeError, TypeError):
                self.CORS_ORIGINS = [self.CORS_ORIGINS]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
