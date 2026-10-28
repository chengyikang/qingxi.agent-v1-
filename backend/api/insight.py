"""Insight API - Module 07"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from engines.insight.engine import insight_engine
from api._helpers import ok

router = APIRouter(prefix="/api/insight", tags=["Insight"])

@router.get("")
async def get_insights(
    user_id: str, insight_type: Optional[str] = None, limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    insights = await insight_engine.get_insights(user_id, insight_type, limit, db)
    return ok({"insights": insights})

@router.post("/generate/weekly")
async def generate_weekly(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await insight_engine.generate_weekly_insight(user_id, db)
    if result:
        return ok(result)
    return ok({"message": "数据不足，无法生成周洞察"})

@router.post("/generate/monthly")
async def generate_monthly(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await insight_engine.generate_monthly_insight(user_id, db)
    if result:
        return ok(result)
    return ok({"message": "数据不足，无法生成月洞察"})
