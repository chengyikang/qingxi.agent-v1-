"""
LifeImport 模型 - Module 01: Life Import Engine
用户人生资料导入记录
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Integer, ForeignKey, JSON, Boolean, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class LifeImport(Base):
    """人生资料导入记录"""
    __tablename__ = "life_imports"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # 导入信息
    source_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # qq_chat/wechat_chat/txt/markdown/pdf/docx/diary/note
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)  # bytes
    
    # 导入状态
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )  # pending/processing/parsed/completed/failed
    
    # 解析结果
    raw_content_preview: Mapped[str | None] = mapped_column(Text, nullable=True)  # 前1000字预览
    parsed_summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # 解析摘要
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 解析出的结构化数据
    
    # 提取结果
    extracted_person_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extracted_event_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extracted_interest_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extracted_memory_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 关联
    created_memory_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 创建的记忆ID
    created_event_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 创建的事件ID
    created_timeline_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 创建的时间轴ID
    
    # 错误信息
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # 元数据
    confidence: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="life_imports")
    
    SOURCE_TYPE_NAMES = {
        "qq_chat": "QQ聊天记录",
        "wechat_chat": "微信聊天记录",
        "txt": "文本文件",
        "markdown": "Markdown文件",
        "pdf": "PDF文档",
        "docx": "Word文档",
        "diary": "日记",
        "note": "笔记",
    }
    
    def __repr__(self) -> str:
        return f"<LifeImport(id={self.id}, source={self.source_type}, status={self.status})>"
