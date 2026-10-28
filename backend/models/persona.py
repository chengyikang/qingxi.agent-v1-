"""
Persona 模型 - Module 03: Persona Engine
用户数字人格：不是标签，是持续成长的人格
包含 Identity、Communication Style、Thinking Style、Emotion Style、Values、Preferences、Current Goals
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Float, ForeignKey, JSON, Integer, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class Persona(Base):
    """数字人格模型"""
    __tablename__ = "personas"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )
    
    # Identity 身份
    identity_summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # 一句话身份概括
    identity_traits: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 性格特质列表
    identity_roles: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 社会角色 ["学生","朋友","程序员"]
    
    # Communication Style 沟通风格
    comm_formality: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 正式度 0-1
    comm_expressiveness: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 表达丰富度
    comm_directness: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 直接程度
    comm_humor: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)  # 幽默倾向
    comm_style_notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # 风格补充说明
    
    # Thinking Style 思维方式
    thinking_analytical: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 分析型
    thinking_creative: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 创造型
    thinking_practical: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 实践型
    thinking_reflective: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 反思型
    thinking_style_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Emotion Style 情绪风格
    emotion_stability: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 情绪稳定性
    emotion_expressiveness: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 情绪表达度
    emotion_sensitivity: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 情绪敏感度
    emotion_optimism: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 乐观倾向
    emotion_style_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotion_patterns: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 情绪模式 [{"pattern":"工作日焦虑","confidence":0.8}]
    
    # Values 价值观
    values_core: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 核心价值观 [{"value":"自由","importance":0.9}]
    values_priorities: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 优先级排序
    
    # Preferences 偏好
    preferences_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 喜欢的话题
    preferences_activities: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 喜欢的活动
    preferences_avoid: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 回避的话题/活动
    preferences_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Current Goals 当前目标
    current_goals: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{"goal":"学Python","status":"active","progress":0.3}]
    
    # 成长追踪
    growth_history: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 人格成长记录
    maturity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 人格成熟度 0-1
    
    # 元数据
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_updated_from: Mapped[str | None] = mapped_column(String(30), nullable=True)  # 最后更新来源
    update_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="persona")
    
    def to_prompt_dict(self) -> dict:
        """转换为 Prompt 可用的字典"""
        return {
            "identity_summary": self.identity_summary or "暂未了解",
            "identity_traits": self.identity_traits or [],
            "comm_formality": self.comm_formality,
            "comm_expressiveness": self.comm_expressiveness,
            "comm_directness": self.comm_directness,
            "thinking_analytical": self.thinking_analytical,
            "thinking_creative": self.thinking_creative,
            "emotion_stability": self.emotion_stability,
            "emotion_optimism": self.emotion_optimism,
            "values_core": self.values_core or [],
            "current_goals": self.current_goals or [],
            "maturity_score": self.maturity_score,
        }
    
    def __repr__(self) -> str:
        return f"<Persona(user_id={self.user_id}, maturity={self.maturity_score})>"
