"""情绪 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from services.emotion import emotion_service
from api._helpers import ok

router = APIRouter(prefix="/api/emotion", tags=["情绪"])

@router.get("")
async def get_emotions(user_id: str, limit: int = 10, db: AsyncSession = Depends(get_db)):
    emotions = await emotion_service.get_recent_emotions(user_id, db, limit)
    return ok({"emotions": emotions})

@router.get("/trend")
async def get_emotion_trend(user_id: str, days: int = 7, db: AsyncSession = Depends(get_db)):
    trend = await emotion_service.get_emotion_trend(user_id, db, days)
    return ok({"trend": trend})

@router.get("/summary")
async def get_emotion_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    summary = await emotion_service.get_emotion_summary(user_id, db)
    return ok(summary)
