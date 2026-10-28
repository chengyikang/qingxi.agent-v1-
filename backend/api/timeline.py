"""Timeline API"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from database.connection import get_db
from models.timeline import Timeline
from api._helpers import ok

router = APIRouter(prefix="/api/timeline", tags=["Timeline"])

@router.get("")
async def get_timeline(
    user_id: str, limit: int = 50,
    entry_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    conditions = [Timeline.user_id == user_id, Timeline.is_active == True]
    if entry_type:
        conditions.append(Timeline.entry_type == entry_type)
    stmt = select(Timeline).where(and_(*conditions)).order_by(desc(Timeline.occurred_at)).limit(limit)
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return ok({
        "entries": [
            {
                "id": e.id, "entry_type": e.entry_type, "title": e.title,
                "description": e.description, "occurred_at": e.occurred_at.isoformat(),
                "category": e.category, "importance": e.importance,
                "emotion_marker": e.emotion_marker,
                "is_shared_with_companion": e.is_shared_with_companion,
                "companion_first": e.companion_first,
            }
            for e in entries
        ],
        "total": len(entries),
    })
