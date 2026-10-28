"""人格状态模型 V0 (保留兼容)"""
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from database.connection import Base
from config import settings


class PersonalityState(Base):
    """人格状态模型 (V0 兼容，V1 由 Persona 模型替代)"""
    __tablename__ = "personality_states"
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    openness: Mapped[int] = mapped_column(Integer, default=settings.INITIAL_OPENNESS, nullable=False)
    initiative: Mapped[int] = mapped_column(Integer, default=settings.INITIAL_INITIATIVE, nullable=False)
    vulnerability: Mapped[int] = mapped_column(Integer, default=settings.INITIAL_VULNERABILITY, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="personality_state")
    
    def get_openness_description(self) -> str:
        if self.openness < 20: return "保持谨慎，只说必要的话"
        elif self.openness < 40: return "适度分享一些想法"
        elif self.openness < 60: return "愿意分享更多自己的想法"
        elif self.openness < 80: return "比较坦诚地表达"
        else: return "非常坦诚，愿意分享内心想法"
    
    def get_initiative_description(self) -> str:
        if self.initiative < 5: return "被动回应，不主动提问"
        elif self.initiative < 10: return "偶尔主动提问"
        elif self.initiative < 15: return "适度主动，会问一些问题"
        elif self.initiative < 20: return "比较主动，经常询问"
        else: return "非常主动，关心地询问"
    
    def get_vulnerability_description(self) -> str:
        if self.vulnerability < 10: return "保持坚强，不表露脆弱"
        elif self.vulnerability < 25: return "偶尔分享一些个人感受"
        elif self.vulnerability < 50: return "愿意分享一些脆弱的想法"
        elif self.vulnerability < 75: return "比较愿意敞开心扉"
        else: return "愿意分享内心深处的感受"
    
    def __repr__(self) -> str:
        return f"<PersonalityState(user_id={self.user_id}, openness={self.openness})>"
