"""用户 API"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.connection import get_db
from models.user import User
from models.trust import TrustProfile
from models.personality import PersonalityState
from api._helpers import ok, err

router = APIRouter(prefix="/api/user", tags=["用户"])

@router.post("/create")
async def create_user(nickname: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        user = User(id=user_id, nickname=nickname, created_at=now, last_active_at=now)
        db.add(user)
        trust = TrustProfile(user_id=user_id, trust_score=10, relationship_stage="stranger", created_at=now)
        db.add(trust)
        personality = PersonalityState(user_id=user_id, openness=10, initiative=5, vulnerability=0, created_at=now)
        db.add(personality)
        await db.commit()
        return ok({"user_id": user_id, "nickname": nickname, "created_at": now.isoformat()})
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ok({"user_id": user.id, "nickname": user.nickname, "created_at": user.created_at.isoformat(), "last_active_at": user.last_active_at.isoformat()})

@router.put("/nickname")
async def update_nickname(user_id: str, nickname: str, db: AsyncSession = Depends(get_db)):
    stmt = update(User).where(User.id == user_id).values(nickname=nickname)
    await db.execute(stmt)
    await db.commit()
    return ok({"user_id": user_id, "nickname": nickname})
