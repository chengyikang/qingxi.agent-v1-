"""
情绪日志模型 V1
V1 升级：新增 intensity, trigger, context_tags
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class EmotionLog(Base):
    """情绪日志模型"""
    __tablename__ = "emotion_logs"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    emotion: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # V1 新增
    intensity: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5 情绪强度
    trigger: Mapped[str | None] = mapped_column(String(200), nullable=True)  # 触发原因
    context_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 上下文标签
    is_negative: Mapped[bool | None] = mapped_column(nullable=True, default=False)  # 是否负面情绪
    
    # 关系
    user = relationship("User", back_populates="emotion_logs")
    
    def __repr__(self) -> str:
        return f"<EmotionLog(id={self.id}, emotion={self.emotion}, confidence={self.confidence})>"
