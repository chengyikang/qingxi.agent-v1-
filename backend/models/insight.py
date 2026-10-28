"""
Insight 模型 - Module 07: Insight Engine
帮助用户了解自己，生成 Weekly/Monthly Insight
Insight 不是建议，Insight 是观察
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Integer, Float, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class Insight(Base):
    """洞察模型"""
    __tablename__ = "insights"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # 洞察基本信息
    insight_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # weekly/monthly/on_demand
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 洞察内容
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)  # 一句话总结
    
    # 洞察分类
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # emotion_pattern/behavior_pattern/growth_observation/relationship_observation/life_observation
    
    # 洞察详情
    observations: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 观察列表
    evidence: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 证据数据
    trends: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 趋势数据
    
    # 时间范围
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # 用户反馈
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5 用户评分
    user_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_helpful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    # 关联
    related_memory_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    related_life_event_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    
    # 元数据
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="insights")
    
    CATEGORY_NAMES = {
        "emotion_pattern": "情绪模式",
        "behavior_pattern": "行为模式",
        "growth_observation": "成长观察",
        "relationship_observation": "关系观察",
        "life_observation": "生活观察",
    }
    
    def __repr__(self) -> str:
        return f"<Insight(id={self.id}, type={self.insight_type}, category={self.category})>"
