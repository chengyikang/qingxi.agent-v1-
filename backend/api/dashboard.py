"""Dashboard API V1 - 新增所有 V1 面板数据"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from database.connection import get_db
from models.user import User
from models.trust import TrustProfile
from models.memory import Memory
from models.chat import ChatHistory
from models.emotion import EmotionLog
from models.persona import Persona
from models.timeline import Timeline
from models.relationship_context import RelationshipContext
from models.insight import Insight
from models.reflection import Reflection
from models.life_profile import LifeProfile
from services.trust import trust_service
from services.emotion import emotion_service
from api._helpers import ok

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("")
async def get_dashboard(user_id: str, db: AsyncSession = Depends(get_db)):
    """V1 完整 Dashboard"""
    now = datetime.utcnow()
    
    # --- 基础统计 ---
    # 信任
    trust_stmt = select(TrustProfile).where(TrustProfile.user_id == user_id)
    trust = (await db.execute(trust_stmt)).scalar_one_or_none()
    trust_score = trust.trust_score if trust else 10
    rel_stage = trust.relationship_stage if trust else "stranger"
    
    # 记忆
    mem_total = (await db.execute(
        select(func.count(Memory.id)).where(Memory.user_id == user_id, Memory.is_active == True)
    )).scalar() or 0
    
    # 按层记忆数
    mem_by_layer = {}
    for layer in ["identity", "preference", "relationship", "life_event", "emotion", "growth"]:
        count = (await db.execute(
            select(func.count(Memory.id)).where(Memory.user_id == user_id, Memory.is_active == True, Memory.layer == layer)
        )).scalar() or 0
        mem_by_layer[layer] = count
    
    # 聊天
    chat_count = (await db.execute(
        select(func.count(ChatHistory.id)).where(ChatHistory.user_id == user_id)
    )).scalar() or 0
    
    # 天数
    user_stmt = select(User).where(User.id == user_id)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    days = (now - user.created_at).days + 1 if user else 0
    
    # --- V1 新增面板 ---
    
    # Persona
    persona_stmt = select(Persona).where(Persona.user_id == user_id)
    persona = (await db.execute(persona_stmt)).scalar_one_or_none()
    persona_data = None
    if persona:
        persona_data = {
            "identity_summary": persona.identity_summary,
            "maturity_score": persona.maturity_score,
            "update_count": persona.update_count,
        }
    
    # Timeline 最近条目
    timeline_stmt = select(Timeline).where(
        Timeline.user_id == user_id, Timeline.is_active == True
    ).order_by(desc(Timeline.occurred_at)).limit(5)
    timeline_entries = (await db.execute(timeline_stmt)).scalars().all()
    timeline_data = [
        {"title": t.title, "entry_type": t.entry_type, "occurred_at": t.occurred_at.isoformat()}
        for t in timeline_entries
    ]
    
    # Relationship 里程碑
    rel_ctx_stmt = select(RelationshipContext).where(
        RelationshipContext.user_id == user_id,
        RelationshipContext.is_milestone == True,
        RelationshipContext.is_active == True,
    ).order_by(desc(RelationshipContext.occurred_at)).limit(5)
    rel_contexts = (await db.execute(rel_ctx_stmt)).scalars().all()
    milestones_data = [
        {"title": r.title, "context_type": r.context_type, "occurred_at": r.occurred_at.isoformat()}
        for r in rel_contexts
    ]
    
    # Insight
    insight_stmt = select(Insight).where(
        Insight.user_id == user_id, Insight.is_active == True
    ).order_by(desc(Insight.created_at)).limit(3)
    insights = (await db.execute(insight_stmt)).scalars().all()
    insight_data = [
        {"title": i.title, "summary": i.summary, "category": i.category}
        for i in insights
    ]
    
    # Reflection
    reflection_stmt = select(Reflection).where(
        Reflection.user_id == user_id, Reflection.is_active == True
    ).order_by(desc(Reflection.created_at)).limit(3)
    reflections = (await db.execute(reflection_stmt)).scalars().all()
    reflection_data = [
        {"title": r.title, "reflection_type": r.reflection_type, "growth_score": r.growth_score}
        for r in reflections
    ]
    
    # Life Profile
    profile_stmt = select(LifeProfile).where(LifeProfile.user_id == user_id)
    profile = (await db.execute(profile_stmt)).scalar_one_or_none()
    profile_data = None
    if profile:
        profile_data = {
            "name": profile.name, "occupation": profile.occupation,
            "completeness_score": profile.completeness_score,
        }
    
    # Emotion Statistics
    emotion_summary = await emotion_service.get_emotion_summary(user_id, db)
    
    # 最近情绪
    emotion_stmt = select(EmotionLog).where(
        EmotionLog.user_id == user_id
    ).order_by(desc(EmotionLog.created_at)).limit(7)
    emotions = (await db.execute(emotion_stmt)).scalars().all()
    recent_emotions = [{"emotion": e.emotion, "confidence": e.confidence, "created_at": e.created_at.isoformat()} for e in emotions]
    
    # Trust Curve (最近 30 天的信任值变化)
    # 简化：返回当前值和阶段进度
    trust_progress = trust_service.get_stage_progress(trust_score) if trust else {}
    
    return ok({
        # V0 兼容
        "relationship_stage": rel_stage,
        "trust_score": trust_score,
        "memory_count": mem_total,
        "chat_count": chat_count,
        "days_together": days,
        "recent_emotions": recent_emotions,
        
        # V1 新增
        "persona": persona_data,
        "timeline": timeline_data,
        "milestones": milestones_data,
        "insights": insight_data,
        "reflections": reflection_data,
        "life_profile": profile_data,
        "memory_statistics": {
            "total": mem_total,
            "by_layer": mem_by_layer,
        },
        "emotion_statistics": emotion_summary,
        "trust_curve": {
            "current_score": trust_score,
            "progress": trust_progress,
        },
    })
