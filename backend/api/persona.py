"""Persona API - Module 03"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from models.persona import Persona
from engines.persona.engine import persona_engine
from models.user import User
from api._helpers import ok, err

router = APIRouter(prefix="/api/persona", tags=["Persona"])

@router.get("")
async def get_persona(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Persona).where(Persona.user_id == user_id)
    result = await db.execute(stmt)
    persona = result.scalar_one_or_none()
    if not persona:
        # 自动创建
        await persona_engine.create_initial_persona(user_id, db)
        result = await db.execute(stmt)
        persona = result.scalar_one_or_none()
    if persona:
        return ok({
            "user_id": persona.user_id,
            "identity_summary": persona.identity_summary,
            "identity_traits": persona.identity_traits,
            "identity_roles": persona.identity_roles,
            "comm_formality": persona.comm_formality,
            "comm_expressiveness": persona.comm_expressiveness,
            "comm_directness": persona.comm_directness,
            "thinking_analytical": persona.thinking_analytical,
            "thinking_creative": persona.thinking_creative,
            "emotion_stability": persona.emotion_stability,
            "emotion_optimism": persona.emotion_optimism,
            "values_core": persona.values_core,
            "current_goals": persona.current_goals,
            "preferences_topics": persona.preferences_topics,
            "maturity_score": persona.maturity_score,
            "update_count": persona.update_count,
            "created_at": persona.created_at.isoformat(),
            "updated_at": persona.updated_at.isoformat(),
        })
    return ok({})

@router.get("/prompt-dict")
async def get_persona_prompt_dict(user_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Persona).where(Persona.user_id == user_id)
    result = await db.execute(stmt)
    persona = result.scalar_one_or_none()
    if persona:
        return ok(persona.to_prompt_dict())
    return ok({})
