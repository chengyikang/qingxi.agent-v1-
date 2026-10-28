"""信任服务"""
from typing import Dict, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.trust import TrustProfile
from trust.engine import trust_engine
from config import settings


class TrustService:
    def __init__(self):
        self.max_trust = settings.MAX_TRUST_SCORE
        self.initial_trust = settings.INITIAL_TRUST_SCORE
    
    async def get_or_create_profile(self, user_id, db):
        stmt = select(TrustProfile).where(TrustProfile.user_id == user_id)
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()
        if not profile:
            profile = TrustProfile(user_id=user_id, trust_score=self.initial_trust, relationship_stage="stranger")
            db.add(profile)
            await db.flush()
        return profile
    
    async def update_trust(self, user_id, message, db):
        profile = await self.get_or_create_profile(user_id, db)
        analysis = await trust_engine.analyze_message(message)
        growth = trust_engine.calculate_trust_growth(analysis)
        old_score = profile.trust_score
        new_score = min(profile.trust_score + growth, self.max_trust)
        profile.trust_score = new_score
        old_stage = profile.relationship_stage
        profile.update_stage()
        new_stage = profile.relationship_stage
        return {
            "old_trust": old_score, "new_trust": new_score, "growth": growth,
            "old_stage": old_stage, "new_stage": new_stage,
            "analysis": analysis, "trust_types": trust_engine.get_trust_type_description(analysis)
        }
    
    async def get_profile(self, user_id, db):
        profile = await self.get_or_create_profile(user_id, db)
        return {
            "user_id": profile.user_id, "trust_score": profile.trust_score,
            "relationship_stage": profile.relationship_stage,
            "created_at": profile.created_at.isoformat(), "updated_at": profile.updated_at.isoformat()
        }
    
    def get_stage_description(self, stage):
        return {"stranger": "刚刚认识", "familiar": "见过几次面", "friend": "我们是朋友", "close_friend": "知己"}.get(stage, "")
    
    def get_stage_progress(self, trust_score):
        stages = {"stranger": (0, 100), "familiar": (100, 300), "friend": (300, 600), "close_friend": (600, 1000)}
        current_stage = "stranger"
        for stage, (min_val, max_val) in stages.items():
            if min_val <= trust_score < max_val:
                current_stage = stage; range_start, range_end = min_val, max_val; break
        else:
            current_stage = "close_friend"; range_start, range_end = 600, 1000
        progress = ((trust_score - range_start) / (range_end - range_start)) * 100
        return {"current_stage": current_stage, "progress_percent": round(progress, 1), "range_start": range_start, "range_end": range_end}


trust_service = TrustService()
