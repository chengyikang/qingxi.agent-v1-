"""情绪服务"""
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from models.emotion import EmotionLog
from emotion.analyzer import emotion_analyzer


class EmotionService:
    async def analyze_and_log(self, user_id, message, db):
        try:
            emotion, confidence = await emotion_analyzer.analyze(message)
            intensity = 1
            if confidence >= 0.8: intensity = 4
            elif confidence >= 0.7: intensity = 3
            elif confidence >= 0.6: intensity = 2
            
            emotion_log = EmotionLog(
                id=str(uuid.uuid4()), user_id=user_id, emotion=emotion,
                confidence=confidence, intensity=intensity,
                is_negative=emotion_analyzer.is_negative(emotion)
            )
            db.add(emotion_log)
            await db.flush()
            return {
                "id": emotion_log.id, "emotion": emotion, "confidence": confidence,
                "intensity": intensity, "is_negative": emotion_log.is_negative,
                "created_at": emotion_log.created_at.isoformat()
            }
        except Exception as e:
            print(f"分析情绪失败: {e}")
            return None
    
    async def get_recent_emotions(self, user_id, db, limit=10):
        stmt = select(EmotionLog).where(EmotionLog.user_id == user_id).order_by(desc(EmotionLog.created_at)).limit(limit)
        result = await db.execute(stmt)
        return [{"id": e.id, "emotion": e.emotion, "confidence": e.confidence, "created_at": e.created_at.isoformat()} for e in result.scalars().all()]
    
    async def get_emotion_trend(self, user_id, db, days=7):
        start_date = datetime.utcnow() - timedelta(days=days)
        stmt = select(func.date(EmotionLog.created_at).label("date"), EmotionLog.emotion, func.count(EmotionLog.id).label("count")).where(
            EmotionLog.user_id == user_id, EmotionLog.created_at >= start_date
        ).group_by(func.date(EmotionLog.created_at), EmotionLog.emotion).order_by("date")
        result = await db.execute(stmt)
        trend = {}
        for row in result.all():
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            if date_str not in trend: trend[date_str] = {"date": date_str, "total": 0}
            trend[date_str][row.emotion] = row.count
            trend[date_str]["total"] += row.count
        return list(trend.values())
    
    async def get_emotion_summary(self, user_id, db):
        trend = await self.get_emotion_trend(user_id, db, days=7)
        stmt = select(EmotionLog.emotion, func.count(EmotionLog.id).label("count")).where(
            EmotionLog.user_id == user_id
        ).group_by(EmotionLog.emotion).order_by(desc("count")).limit(1)
        result = await db.execute(stmt)
        row = result.scalar_one_or_none()
        dominant = row.emotion if row else "neutral"
        return {"dominant_emotion": dominant, "weekly_trend": trend, "needs_attention": dominant in ["sad", "anxious", "angry", "lonely"]}


emotion_service = EmotionService()
