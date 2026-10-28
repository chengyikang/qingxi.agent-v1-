"""人格服务 V0 (兼容)"""
from typing import Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.personality import PersonalityState
from personality.engine import personality_engine
from config import settings


class PersonalityService:
    def __init__(self):
        self.initial_values = {"openness": settings.INITIAL_OPENNESS, "initiative": settings.INITIAL_INITIATIVE, "vulnerability": settings.INITIAL_VULNERABILITY}
    
    async def get_or_create_state(self, user_id, db):
        stmt = select(PersonalityState).where(PersonalityState.user_id == user_id)
        result = await db.execute(stmt)
        state = result.scalar_one_or_none()
        if not state:
            state = PersonalityState(user_id=user_id, **self.initial_values)
            db.add(state)
            await db.flush()
        return state
    
    async def update_from_trust_growth(self, user_id, trust_growth, db):
        state = await self.get_or_create_state(user_id, db)
        current = {"openness": state.openness, "initiative": state.initiative, "vulnerability": state.vulnerability}
        growth = personality_engine.calculate_growth(trust_growth)
        new_state = personality_engine.apply_growth(current, growth)
        state.openness = new_state["openness"]
        state.initiative = new_state["initiative"]
        state.vulnerability = new_state["vulnerability"]
        return {"old_state": current, "growth": growth, "new_state": new_state}
    
    async def get_state(self, user_id, db):
        state = await self.get_or_create_state(user_id, db)
        current = {"openness": state.openness, "initiative": state.initiative, "vulnerability": state.vulnerability}
        return {
            "user_id": state.user_id, **current,
            "description": personality_engine.get_personality_description(current),
            "guidance": personality_engine.get_response_guidance(current),
        }


personality_service = PersonalityService()
