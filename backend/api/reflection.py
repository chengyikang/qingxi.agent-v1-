"""Reflection API - Module 08"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from engines.reflection.engine import reflection_engine
from api._helpers import ok

router = APIRouter(prefix="/api/reflection", tags=["Reflection"])

@router.get("")
async def get_reflections(
    user_id: str, reflection_type: Optional[str] = None, limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    reflections = await reflection_engine.get_reflections(user_id, reflection_type, limit, db)
    return ok({"reflections": reflections})

@router.post("/generate/weekly")
async def generate_weekly(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await reflection_engine.generate_weekly_reflection(user_id, db)
    if result:
        return ok(result)
    return ok({"message": "数据不足，无法生成周回顾"})

@router.post("/generate/monthly")
async def generate_monthly(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await reflection_engine.generate_monthly_reflection(user_id, db)
    if result:
        return ok(result)
    return ok({"message": "数据不足，无法生成月回顾"})

@router.post("/generate/yearly")
async def generate_yearly(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await reflection_engine.generate_yearly_reflection(user_id, db)
    if result:
        return ok(result)
    return ok({"message": "数据不足，无法生成年回顾"})
