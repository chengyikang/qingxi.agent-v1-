"""
QingXi V1 配置文件
管理所有环境变量和配置项
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/qingxi"
    
    # OpenAI API 配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # ChromaDB 配置
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 应用配置
    APP_NAME: str = "QingXi V1"
    DEBUG: bool = True
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 50
    MAX_MEMORY_RETRIEVAL: int = 10
    
    # 信任系统配置
    INITIAL_TRUST_SCORE: int = 10
    MAX_TRUST_SCORE: int = 1000
    
    # 人格初始值配置
    INITIAL_OPENNESS: int = 10
    INITIAL_INITIATIVE: int = 5
    INITIAL_VULNERABILITY: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
