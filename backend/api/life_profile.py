"""Life Profile API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from models.life_profile import LifeProfile
from api._helpers import ok

router = APIRouter(prefix="/api/life-profile", tags=["Life Profile"])

@router.get("")
async def get_life_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(LifeProfile).where(LifeProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        return ok({"message": "人生画像尚未生成"})
    return ok({
        "name": profile.name,
        "age_range": profile.age_range,
        "occupation": profile.occupation,
        "location": profile.location,
        "interests": profile.interests,
        "goals_short_term": profile.goals_short_term,
        "goals_long_term": profile.goals_long_term,
        "dreams": profile.dreams,
        "important_people": profile.important_people,
        "values": profile.values,
        "thinking_style": profile.thinking_style,
        "communication_style": profile.communication_style,
        "social_style": profile.social_style,
        "emotion_patterns": profile.emotion_patterns,
        "completeness_score": profile.completeness_score,
        "updated_at": profile.updated_at.isoformat(),
    })
