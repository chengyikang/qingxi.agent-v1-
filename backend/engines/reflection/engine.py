"""
Module 08: Reflection Engine
帮助用户记录成长，自动生成 Weekly/Monthly/Yearly Reflection
Reflection 不是总结，Reflection 是陪伴用户成长
"""
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ReflectionEngine:
    """反思/回顾引擎"""
    
    async def generate_weekly_reflection(
        self, user_id: str, db
    ) -> Optional[Dict[str, Any]]:
        """生成周反思"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        return await self._generate_reflection(
            user_id, "weekly", start_date, end_date, db
        )
    
    async def generate_monthly_reflection(
        self, user_id: str, db
    ) -> Optional[Dict[str, Any]]:
        """生成月反思"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        return await self._generate_reflection(
            user_id, "monthly", start_date, end_date, db
        )
    
    async def generate_yearly_reflection(
        self, user_id: str, db
    ) -> Optional[Dict[str, Any]]:
        """生成年反思"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        return await self._generate_reflection(
            user_id, "yearly", start_date, end_date, db
        )
    
    async def _generate_reflection(
        self,
        user_id: str,
        reflection_type: str,
        period_start: datetime,
        period_end: datetime,
        db,
    ) -> Optional[Dict[str, Any]]:
        """生成反思"""
        # 1. 收集期间数据
        data = await self._collect_data(user_id, period_start, period_end, db)
        
        if not data.get("has_data"):
            return None
        
        # 2. 生成反思内容
        try:
            content = await self._generate_with_llm(
                user_id, reflection_type, data, period_start, period_end
            )
        except Exception as e:
            logger.warning(f"LLM 生成反思失败: {e}")
            content = self._generate_with_rules(reflection_type, data)
        
        # 3. 保存
        from models.reflection import Reflection
        reflection = Reflection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            reflection_type=reflection_type,
            title=content.get("title", f"{reflection_type} 回顾"),
            content=content.get("content", ""),
            highlights=content.get("highlights", []),
            challenges=content.get("challenges", []),
            growth_points=content.get("growth_points", []),
            gratitude=content.get("gratitude", []),
            learnings=content.get("learnings", []),
            looking_forward=content.get("looking_forward", ""),
            growth_score=content.get("growth_score"),
            mood_overall=content.get("mood_overall"),
            energy_level=content.get("energy_level"),
            period_start=period_start,
            period_end=period_end,
        )
        db.add(reflection)
        await db.flush()
        
        return {
            "id": reflection.id,
            "title": reflection.title,
            "content": reflection.content,
            "reflection_type": reflection_type,
        }
    
    async def _collect_data(self, user_id, start, end, db) -> Dict:
        """收集期间数据"""
        from models.chat import ChatHistory
        from models.emotion import EmotionLog
        from models.life_event import LifeEvent
        from models.insight import Insight
        from sqlalchemy import select, func, desc, and_
        
        data = {"has_data": False}
        
        # 消息数
        stmt = select(func.count(ChatHistory.id)).where(
            ChatHistory.user_id == user_id,
            ChatHistory.role == "user",
            ChatHistory.created_at >= start,
            ChatHistory.created_at <= end,
        )
        data["chat_count"] = (await db.execute(stmt)).scalar() or 0
        
        # 情绪分布
        stmt = select(EmotionLog.emotion, func.count(EmotionLog.id).label("count")).where(
            EmotionLog.user_id == user_id,
            EmotionLog.created_at >= start,
        ).group_by(EmotionLog.emotion)
        result = await db.execute(stmt)
        data["emotions"] = {row.emotion: row.count for row in result.all()}
        
        # 人生事件
        stmt = select(LifeEvent).where(
            LifeEvent.user_id == user_id,
            LifeEvent.is_active == True,
            LifeEvent.created_at >= start,
        ).order_by(desc(LifeEvent.impact_level)).limit(10)
        result = await db.execute(stmt)
        data["life_events"] = [
            {"title": e.title, "type": e.event_type, "impact": e.impact_level}
            for e in result.scalars().all()
        ]
        
        # 近期洞察
        stmt = select(Insight).where(
            Insight.user_id == user_id,
            Insight.is_active == True,
            Insight.created_at >= start,
        ).order_by(desc(Insight.created_at)).limit(5)
        result = await db.execute(stmt)
        data["insights"] = [
            {"title": i.title, "summary": i.summary}
            for i in result.scalars().all()
        ]
        
        # 活跃天数
        stmt = select(func.count(func.date(ChatHistory.created_at).distinct())).where(
            ChatHistory.user_id == user_id,
            ChatHistory.created_at >= start,
        )
        data["active_days"] = (await db.execute(stmt)).scalar() or 0
        
        data["has_data"] = data["chat_count"] > 0
        return data
    
    async def _generate_with_llm(self, user_id, reflection_type, data, start, end) -> Dict:
        """LLM 生成反思"""
        from services.llm import llm_service
        
        period_labels = {"weekly": "一周", "monthly": "一个月", "yearly": "一年"}
        period = period_labels.get(reflection_type, "一段时间")
        days = (end - start).days
        
        prompt = f"""请为用户生成一份{period}的成长回顾。

回顾不是总结，回顾是陪伴成长。用温暖、真诚的语气。

数据：
- 天数：{days}天
- 活跃天数：{data.get('active_days', 0)}天
- 对话次数：{data.get('chat_count', 0)}次
- 情绪分布：{json.dumps(data.get('emotions', {}), ensure_ascii=False)}
- 重要事件：{json.dumps(data.get('life_events', []), ensure_ascii=False)}
- 近期洞察：{json.dumps(data.get('insights', []), ensure_ascii=False)}

请返回 JSON：
{{
  "title": "回顾标题",
  "content": "回顾正文（150-400字，温暖的陪伴感）",
  "highlights": ["亮点1", "亮点2"],
  "challenges": ["挑战1", "挑战2"],
  "growth_points": ["成长1", "成长2"],
  "gratitude": ["感恩1", "感恩2"],
  "learnings": ["学到1", "学到2"],
  "looking_forward": "展望",
  "growth_score": 0.5,
  "mood_overall": "mixed",
  "energy_level": 0.6
}}

只返回 JSON。"""
        
        result = await llm_service.analysis(
            prompt=prompt,
            system_message="你是成长陪伴专家，善于用温暖的语气帮助用户回顾成长。只返回 JSON。"
        )
        
        if isinstance(result, str):
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            return json.loads(result.strip())
        return result
    
    def _generate_with_rules(self, reflection_type, data) -> Dict:
        """规则生成反思"""
        period_labels = {"weekly": "这周", "monthly": "这个月", "yearly": "这一年"}
        period = period_labels.get(reflection_type, "这段时间")
        
        emotions = data.get("emotions", {})
        total = sum(emotions.values()) if emotions else 0
        
        if total > 0:
            positive = emotions.get("happy", 0)
            negative = emotions.get("sad", 0) + emotions.get("anxious", 0) + emotions.get("angry", 0)
            positive_ratio = positive / total
        else:
            positive_ratio = 0.5
        
        content = f"{period}，我们一起走过了{data.get('active_days', 0)}天。"
        if positive_ratio > 0.4:
            content += "有很多开心的时刻，也有需要照顾自己的时候。"
        else:
            content += "虽然有些不容易，但你一直在往前走。"
        content += "希望下一段时间，我们继续一起成长。"
        
        return {
            "title": f"{period}的成长回顾",
            "content": content,
            "highlights": [],
            "challenges": [],
            "growth_points": [],
            "gratitude": [],
            "learnings": [],
            "looking_forward": "",
            "growth_score": 0.5,
            "mood_overall": "mixed",
            "energy_level": 0.5,
        }
    
    async def get_reflections(
        self, user_id: str, reflection_type: Optional[str] = None, limit: int = 10, db=None
    ) -> List[Dict]:
        """获取反思列表"""
        from models.reflection import Reflection
        from sqlalchemy import select, desc, and_
        
        conditions = [Reflection.user_id == user_id, Reflection.is_active == True]
        if reflection_type:
            conditions.append(Reflection.reflection_type == reflection_type)
        
        stmt = select(Reflection).where(and_(*conditions)).order_by(
            desc(Reflection.created_at)
        ).limit(limit)
        result = await db.execute(stmt)
        reflections = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "reflection_type": r.reflection_type,
                "title": r.title,
                "content": r.content,
                "highlights": r.highlights,
                "challenges": r.challenges,
                "growth_points": r.growth_points,
                "growth_score": r.growth_score,
                "period_start": r.period_start.isoformat(),
                "period_end": r.period_end.isoformat(),
                "created_at": r.created_at.isoformat(),
            }
            for r in reflections
        ]


# 全局实例
reflection_engine = ReflectionEngine()
