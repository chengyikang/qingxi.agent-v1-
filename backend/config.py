"""
QingXi V1 配置文件
管理所有环境变量和配置项
"""
import os
from pydantic_settings import BaseSettings
from typing import List, Optional


# LLM 提供商预设配置
LLM_PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
    },
    "moonshot": {
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-flash",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-turbo",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
    },
    "custom": {
        "base_url": "",
        "default_model": "",
    },
}


class Settings(BaseSettings):
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/qingxi"
    
    # LLM 提供商配置
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""
    
    # 向后兼容
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = ""
    OPENAI_BASE_URL: str = ""
    
    # ChromaDB 配置
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 应用配置
    APP_NAME: str = "QingXi V1"
    APP_VERSION: str = "1.0.0"
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
    
    # Memory 6 层配置
    MEMORY_LAYERS: List[str] = [
        "identity",        # 身份层：核心身份信息
        "preference",      # 偏好层：喜好和习惯
        "relationship",    # 关系层：与他人的关系
        "life_event",      # 事件层：重要人生事件
        "emotion",         # 情绪层：情绪模式和特点
        "growth",          # 成长层：成长经历和感悟
    ]
    
    # Memory 可信度阈值
    MEMORY_MIN_CONFIDENCE: float = 0.3
    MEMORY_DEFAULT_CONFIDENCE: float = 0.7
    MEMORY_HIGH_CONFIDENCE: float = 0.9
    
    # Persona 更新配置
    PERSONA_UPDATE_INTERVAL_HOURS: int = 24
    PERSONA_GROWTH_RATE: float = 0.05
    
    # Insight 配置
    INSIGHT_WEEKLY_DAY: int = 0  # 0=Monday
    INSIGHT_MONTHLY_DAY: int = 1  # 1st of month
    
    # Reflection 配置
    REFLECTION_WEEKLY_DAY: int = 0
    REFLECTION_MONTHLY_DAY: int = 1
    REFLECTION_YEARLY_MONTH: int = 12  # December
    
    # Life Import 支持的格式
    SUPPORTED_IMPORT_FORMATS: List[str] = [
        "txt", "markdown", "pdf", "docx",
        "qq_chat", "wechat_chat", "diary", "note"
    ]
    
    # Life Import 文件大小限制 (MB)
    MAX_IMPORT_FILE_SIZE_MB: int = 50
    
    def get_llm_config(self) -> dict:
        """解析 LLM 配置，合并提供商预设和用户覆盖"""
        api_key = self.LLM_API_KEY or self.OPENAI_API_KEY or ""
        provider = self.LLM_PROVIDER.lower()
        preset = LLM_PROVIDERS.get(provider, LLM_PROVIDERS["openai"])
        base_url = (
            self.LLM_BASE_URL 
            or self.OPENAI_BASE_URL 
            or preset["base_url"]
        )
        model = (
            self.LLM_MODEL 
            or self.OPENAI_MODEL 
            or preset["default_model"]
        )
        return {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
            "provider": provider,
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
