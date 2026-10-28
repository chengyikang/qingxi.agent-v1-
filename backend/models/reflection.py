"""
Reflection 模型 - Module 08: Reflection Engine
帮助用户记录成长，自动生成 Weekly/Monthly/Yearly Reflection
Reflection 不是总结，Reflection 是陪伴用户成长
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Integer, Float, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class Reflection(Base):
    """反思/回顾模型"""
    __tablename__ = "reflections"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # 反思基本信息
    reflection_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # weekly/monthly/yearly/on_demand
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 反思内容结构
    highlights: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 这段时间的亮点
    challenges: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 面对的挑战
    growth_points: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 成长点
    gratitude: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 感恩的事
    learnings: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 学到的
    looking_forward: Mapped[str | None] = mapped_column(Text, nullable=True)  # 展望
    
    # 成长评估
    growth_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 成长评分 0-1
    mood_overall: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 整体心情
    energy_level: Mapped[float | None] = mapped_column(Float, nullable=True)  # 能量水平 0-1
    
    # 时间范围
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # 关联
    related_insight_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    related_life_event_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    related_memory_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    
    # 用户补充
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # 用户自己补充的
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # 元数据
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="reflections")
    
    def __repr__(self) -> str:
        return f"<Reflection(id={self.id}, type={self.reflection_type})>"
