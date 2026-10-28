"""
LifeProfile 模型
用户人生画像：身份、兴趣、目标、重要人物、成长轨迹、价值观、思维方式、沟通方式、情绪特点
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Float, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class LifeProfile(Base):
    """人生画像模型"""
    __tablename__ = "life_profiles"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    
    # 基本身份
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    age_range: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "20-25"
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    education: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # 兴趣和目标
    interests: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{"name":"编程","level":"high","category":"tech"}]
    goals_short_term: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 短期目标
    goals_long_term: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 长期目标
    dreams: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 梦想
    
    # 重要人物
    important_people: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{"name":"妈妈","relation":"family","closeness":0.9}]
    
    # 成长轨迹
    growth_trajectory: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{"period":"2024","summary":"...","growth_areas":["职业"]}]
    life_chapters: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 人生章节
    
    # 价值观
    values: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{"value":"自由","importance":0.9}]
    beliefs: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 信念
    
    # 思维方式
    thinking_style: Mapped[str | None] = mapped_column(Text, nullable=True)  # 思维方式概述
    decision_style: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 决策风格
    
    # 沟通方式
    communication_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    social_style: Mapped[str | None] = mapped_column(String(50), nullable=True)  # introvert/ambivert/extrovert
    
    # 情绪特点
    emotion_patterns: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 情绪模式
    stress_triggers: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 压力来源
    coping_mechanisms: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 应对方式
    
    # 统计
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 完整度 0-1
    last_enriched_from: Mapped[str | None] = mapped_column(String(30), nullable=True)
    
    # 元数据
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="life_profile")
    
    def calculate_completeness(self) -> float:
        """计算画像完整度"""
        fields = [
            self.name, self.occupation, self.location, self.education,
            self.interests, self.goals_short_term, self.dreams,
            self.important_people, self.values, self.thinking_style,
            self.communication_style, self.emotion_patterns
        ]
        filled = sum(1 for f in fields if f is not None and f != [] and f != "")
        return round(filled / len(fields), 2)
    
    def __repr__(self) -> str:
        return f"<LifeProfile(user_id={self.user_id}, completeness={self.completeness_score})>"
