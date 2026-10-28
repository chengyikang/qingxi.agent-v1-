"""Relationship API - Module 05"""
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from engines.relationship.engine import relationship_engine
from services.trust import trust_service
from api._helpers import ok

router = APIRouter(prefix="/api/relationship", tags=["Relationship"])

@router.get("/context")
async def get_relationship_context(user_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    contexts = await relationship_engine.get_relationship_context(user_id, db, limit)
    trust = await trust_service.get_or_create_profile(user_id, db)
    return ok({
        "trust_score": trust.trust_score,
        "relationship_stage": trust.relationship_stage,
        "contexts": contexts,
    })

@router.get("/milestones")
async def get_milestones(user_id: str, db: AsyncSession = Depends(get_db)):
    from models.relationship_context import RelationshipContext
    from sqlalchemy import select, desc
    stmt = select(RelationshipContext).where(
        RelationshipContext.user_id == user_id,
        RelationshipContext.is_milestone == True,
        RelationshipContext.is_active == True,
    ).order_by(desc(RelationshipContext.occurred_at))
    result = await db.execute(stmt)
    milestones = result.scalars().all()
    return ok({
        "milestones": [
            {
                "id": m.id, "context_type": m.context_type, "title": m.title,
                "occurred_at": m.occurred_at.isoformat(),
                "significance": m.significance, "milestone_type": m.milestone_type,
            }
            for m in milestones
        ]
    })
