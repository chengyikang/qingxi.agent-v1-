"""
聊天历史模型 V1
V1 升级：新增 emotion_type, intent, memory_ids, persona_snapshot
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class ChatHistory(Base):
    """聊天历史模型"""
    __tablename__ = "chat_histories"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" 或 "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # V1 新增字段
    emotion_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 当前消息情绪
    emotion_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 消息意图：chat/share/ask/reflect
    memory_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 本轮提取的记忆ID
    persona_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 当时的人格快照
    trust_score_at: Mapped[int | None] = mapped_column(nullable=True)  # 当时的信任值
    
    # 关系
    user = relationship("User", back_populates="chat_histories")
    
    def __repr__(self) -> str:
        return f"<ChatHistory(id={self.id}, role={self.role}, user_id={self.user_id})>"
