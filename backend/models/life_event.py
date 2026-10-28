"""
LifeEvent 模型 - Module 02/04
用户人生事件：重要时刻、转折点、成长节点
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Integer, Float, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class LifeEvent(Base):
    """人生事件模型"""
    __tablename__ = "life_events"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # 事件基本信息
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # 事件标题
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # 事件描述
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # milestone/challenge/achievement/transition/relationship/daily
    
    # 时间信息
    event_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)  # 事件发生时间
    event_date_precision: Mapped[str] = mapped_column(
        String(10), default="day", nullable=False
    )  # year/month/day/exact
    
    # 影响和情感
    impact_level: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 影响程度 1-10
    emotion_at_event: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 当时情绪
    emotion_after: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 事后情绪
    growth_significance: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 成长意义 0-1
    
    # 人物和地点
    people_involved: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 相关人物
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # 来源
    source: Mapped[str] = mapped_column(String(30), default="chat", nullable=False)  # chat/import/parser/manual
    source_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # 来源记录ID
    
    # 关联
    related_memory_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 关联记忆
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 标签
    
    # 元数据
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="life_events")
    
    EVENT_TYPE_NAMES = {
        "milestone": "里程碑",
        "challenge": "挑战",
        "achievement": "成就",
        "transition": "转折",
        "relationship": "关系",
        "daily": "日常",
    }
    
    def __repr__(self) -> str:
        return f"<LifeEvent(id={self.id}, title={self.title}, type={self.event_type})>"
