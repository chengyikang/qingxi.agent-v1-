"""
RelationshipContext 模型 - Module 05: Relationship Engine
共同经历记录：第一次聊天、第一次聊梦想、第一次分享烦恼等
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Integer, Float, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class RelationshipContext(Base):
    """关系上下文模型 - 共同经历记录"""
    __tablename__ = "relationship_contexts"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # 共同经历类型
    context_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # first_chat/first_dream/first_trouble/first_laugh/deep_conversation/...
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # "第一次聊梦想"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # 时间
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # 关联对话
    chat_message_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    chat_summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # 那次对话的摘要
    
    # 情感
    emotion_at: Mapped[str | None] = mapped_column(String(20), nullable=True)
    significance: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 意义度 0-1
    
    # 里程碑标记
    is_milestone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    milestone_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # stranger_to_familiar/familiar_to_friend/...
    
    # 元数据
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="relationship_contexts")
    
    # 预定义的关系上下文类型
    PREDEFINED_TYPES = {
        "first_chat": "第一次聊天",
        "first_name_exchange": "第一次交换称呼",
        "first_dream": "第一次聊梦想",
        "first_trouble": "第一次分享烦恼",
        "first_laugh": "第一次一起笑",
        "first_deep_conversation": "第一次深入对话",
        "first_vulnerability": "第一次表露脆弱",
        "first_gratitude": "第一次表达感谢",
        "first_argument": "第一次分歧",
        "first_reconciliation": "第一次和好",
        "trust_milestone": "信任里程碑",
        "emotion_milestone": "情绪里程碑",
    }
    
    def __repr__(self) -> str:
        return f"<RelationshipContext(id={self.id}, type={self.context_type})>"
