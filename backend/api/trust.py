"""信任 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from services.trust import trust_service
from models.user import User
from api._helpers import ok, err

router = APIRouter(prefix="/api/trust", tags=["信任"])

@router.get("")
async def get_trust_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="用户不存在")
    profile = await trust_service.get_profile(user_id, db)
    return ok(profile)
