"""
记忆模型 V1 - Life Memory
V1 重大升级：6层分类、来源、可信度、关联关系、更新时间
Memory 不是聊天记录，Memory 是人生
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Text, Integer, Float, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base


class Memory(Base):
    """记忆模型 - V1 六层人生记忆"""
    __tablename__ = "memories"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # V0 兼容字段
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    importance: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # V1 新增：6 层分类
    layer: Mapped[str] = mapped_column(
        String(30), nullable=False, default="identity", index=True
    )  # identity/preference/relationship/life_event/emotion/growth
    
    # V1 新增：来源追踪
    source: Mapped[str] = mapped_column(
        String(30), nullable=False, default="chat", index=True
    )  # chat/import/persona/insight/reflection/system
    
    # V1 新增：可信度
    confidence: Mapped[float] = mapped_column(
        Float, default=0.7, nullable=False
    )  # 0.0-1.0，越高越可信
    
    # V1 新增：时间关联
    event_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 事件发生时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # V1 新增：关联关系
    related_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # persona/life_event/timeline/insight
    related_entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    
    # V1 新增：元数据
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # 软删除
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 版本号，修改时递增
    
    # 关系
    user = relationship("User", back_populates="memories")
    
    # 层级中文映射
    LAYER_NAMES = {
        "identity": "身份",
        "preference": "偏好",
        "relationship": "关系",
        "life_event": "事件",
        "emotion": "情绪",
        "growth": "成长",
    }
    
    # 来源中文映射
    SOURCE_NAMES = {
        "chat": "对话",
        "import": "导入",
        "persona": "人格",
        "insight": "洞察",
        "reflection": "反思",
        "system": "系统",
    }
    
    def get_layer_name(self) -> str:
        return self.LAYER_NAMES.get(self.layer, self.layer)
    
    def get_source_name(self) -> str:
        return self.SOURCE_NAMES.get(self.source, self.source)
    
    def __repr__(self) -> str:
        return f"<Memory(id={self.id}, layer={self.layer}, category={self.category})>"
