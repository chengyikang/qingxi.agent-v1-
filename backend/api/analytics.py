"""Analytics API V1"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database.connection import get_db
from models.user import User
from models.chat import ChatHistory
from models.trust import TrustProfile
from api._helpers import ok

router = APIRouter(prefix="/api/analytics", tags=["数据分析"])

@router.get("")
async def get_analytics(user_id: str, db: AsyncSession = Depends(get_db)):
    total_chats = (await db.execute(
        select(func.count(ChatHistory.id)).where(ChatHistory.user_id == user_id, ChatHistory.role == "user")
    )).scalar() or 0
    trust = (await db.execute(select(TrustProfile).where(TrustProfile.user_id == user_id))).scalar_one_or_none()
    trust_score = trust.trust_score if trust else 10
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    days = (datetime.utcnow() - user.created_at).days + 1 if user else 0
    return ok({
        "total_chats": total_chats,
        "consecutive_days": days,
        "trust_growth_speed": round(trust_score / max(days, 1), 1),
        "current_trust": trust_score,
    })

@router.get("/engagement")
async def get_engagement(user_id: str, days: int = Query(30, ge=7, le=90), db: AsyncSession = Depends(get_db)):
    start = datetime.utcnow() - timedelta(days=days)
    msg_count = (await db.execute(
        select(func.count(ChatHistory.id)).where(ChatHistory.user_id == user_id, ChatHistory.created_at >= start)
    )).scalar() or 0
    return ok({"period_days": days, "message_count": msg_count, "avg_per_day": round(msg_count / days, 1)})
