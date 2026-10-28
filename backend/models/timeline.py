"""
Timeline 模型
人生时间轴：不是历史，是共同经历
记录人生事件、共同经历、成长节点
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Integer, Float, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class Timeline(Base):
    """时间轴模型"""
    __tablename__ = "timelines"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # 时间轴条目
    entry_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # life_event/shared_experience/growth_node/trust_milestone/conversation_milestone
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # 时间
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    occurred_at_precision: Mapped[str] = mapped_column(String(10), default="day", nullable=False)
    
    # 分类和重要性
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # relationship/growth/life/career/emotion
    importance: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # 关联
    related_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    related_life_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    
    # 情感标记
    emotion_marker: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 这一刻的情绪
    
    # 共同经历特有
    is_shared_with_companion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否与清溪的共同经历
    companion_first: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 第一次XXX（如"第一次聊梦想"）
    
    # 元数据
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="timeline_entries")
    
    ENTRY_TYPE_NAMES = {
        "life_event": "人生事件",
        "shared_experience": "共同经历",
        "growth_node": "成长节点",
        "trust_milestone": "信任里程碑",
        "conversation_milestone": "对话里程碑",
    }
    
    def __repr__(self) -> str:
        return f"<Timeline(id={self.id}, type={self.entry_type}, title={self.title})>"
