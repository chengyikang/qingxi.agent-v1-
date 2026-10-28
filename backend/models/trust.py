"""信任档案模型 V0 (保留兼容)"""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base
from config import settings


class TrustProfile(Base):
    """信任档案模型"""
    __tablename__ = "trust_profiles"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    trust_score: Mapped[int] = mapped_column(Integer, default=settings.INITIAL_TRUST_SCORE, nullable=False)
    relationship_stage: Mapped[str] = mapped_column(String(50), default="stranger", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="trust_profile")
    
    def get_relationship_stage(self) -> str:
        if self.trust_score < 100: return "stranger"
        elif self.trust_score < 300: return "familiar"
        elif self.trust_score < 600: return "friend"
        else: return "close_friend"
    
    def update_stage(self):
        self.relationship_stage = self.get_relationship_stage()
    
    def __repr__(self) -> str:
        return f"<TrustProfile(user_id={self.user_id}, trust_score={self.trust_score}, stage={self.relationship_stage})>"
