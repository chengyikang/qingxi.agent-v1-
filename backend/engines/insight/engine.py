"""
Module 07: Insight Engine
帮助用户了解自己，生成 Weekly/Monthly Insight
Insight 不是建议，Insight 是观察
"""
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InsightEngine:
    """洞察引擎"""
    
    async def generate_weekly_insight(
        self,
        user_id: str,
        db,
    ) -> Optional[Dict[str, Any]]:
        """生成周洞察"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        return await self._generate_insight(
            user_id=user_id,
            insight_type="weekly",
            period_start=start_date,
            period_end=end_date,
            db=db,
        )
    
    async def generate_monthly_insight(
        self,
        user_id: str,
        db,
    ) -> Optional[Dict[str, Any]]:
        """生成月洞察"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        return await self._generate_insight(
            user_id=user_id,
            insight_type="monthly",
            period_start=start_date,
            period_end=end_date,
            db=db,
        )
    
    async def _generate_insight(
        self,
        user_id: str,
        insight_type: str,
        period_start: datetime,
        period_end: datetime,
        db,
    ) -> Optional[Dict[str, Any]]:
        """生成洞察"""
        # 1. 收集数据
        data = await self._collect_period_data(user_id, period_start, period_end, db)
        
        if not data["has_data"]:
            logger.info(f"用户 {user_id} 在 {insight_type} 期间无数据，跳过洞察生成")
            return None
        
        # 2. 尝试 LLM 生成
        try:
            insight_content = await self._generate_with_llm(
                user_id, insight_type, data, period_start, period_end
            )
        except Exception as e:
            logger.warning(f"LLM 生成洞察失败: {e}，使用规则生成")
            insight_content = self._generate_with_rules(insight_type, data)
        
        # 3. 保存洞察
        from models.insight import Insight
        insight = Insight(
            id=str(uuid.uuid4()),
            user_id=user_id,
            insight_type=insight_type,
            title=insight_content.get("title", f"{insight_type} 洞察"),
            content=insight_content.get("content", ""),
            summary=insight_content.get("summary", ""),
            category=insight_content.get("category", "life_observation"),
            observations=insight_content.get("observations", []),
            evidence=insight_content.get("evidence", {}),
            period_start=period_start,
            period_end=period_end,
            confidence=insight_content.get("confidence", 0.6),
        )
        db.add(insight)
        await db.flush()
        
        return {
            "id": insight.id,
            "title": insight.title,
            "content": insight.content,
            "summary": insight.summary,
            "category": insight.category,
        }
    
    async def _collect_period_data(
        self,
        user_id: str,
        start: datetime,
        end: datetime,
        db,
    ) -> Dict[str, Any]:
        """收集期间数据"""
        from models.chat import ChatHistory
        from models.emotion import EmotionLog
        from models.memory import Memory
        from sqlalchemy import select, func, desc, and_
        
        data = {"has_data": False}
        
        # 聊天数
        chat_stmt = select(func.count(ChatHistory.id)).where(
            ChatHistory.user_id == user_id,
            ChatHistory.role == "user",
            ChatHistory.created_at >= start,
            ChatHistory.created_at <= end,
        )
        chat_count = (await db.execute(chat_stmt)).scalar() or 0
        data["chat_count"] = chat_count
        
        # 情绪分布
        emotion_stmt = select(
            EmotionLog.emotion, func.count(EmotionLog.id).label("count")
        ).where(
            EmotionLog.user_id == user_id,
            EmotionLog.created_at >= start,
            EmotionLog.created_at <= end,
        ).group_by(EmotionLog.emotion)
        emotion_result = await db.execute(emotion_stmt)
        data["emotion_distribution"] = {row.emotion: row.count for row in emotion_result.all()}
        
        # 新增记忆数
        mem_stmt = select(func.count(Memory.id)).where(
            Memory.user_id == user_id,
            Memory.created_at >= start,
            Memory.created_at <= end,
            Memory.is_active == True,
        )
        data["new_memory_count"] = (await db.execute(mem_stmt)).scalar() or 0
        
        # 主导情绪
        if data["emotion_distribution"]:
            data["dominant_emotion"] = max(
                data["emotion_distribution"], key=data["emotion_distribution"].get
            )
        else:
            data["dominant_emotion"] = "neutral"
        
        # 近期对话摘要
        recent_stmt = select(ChatHistory.content).where(
            ChatHistory.user_id == user_id,
            ChatHistory.role == "user",
            ChatHistory.created_at >= start,
        ).order_by(desc(ChatHistory.created_at)).limit(20)
        recent_result = await db.execute(recent_stmt)
        data["recent_messages"] = [row.content for row in recent_result.all()]
        
        data["has_data"] = chat_count > 0
        return data
    
    async def _generate_with_llm(
        self, user_id, insight_type, data, period_start, period_end
    ) -> Dict[str, Any]:
        """LLM 生成洞察"""
        from services.llm import llm_service
        
        period_label = "一周" if insight_type == "weekly" else "一个月"
        
        prompt = f"""请根据以下数据，为用户生成一个{period_label}的生活洞察。

洞察不是建议，洞察是观察。请用温暖的语气观察用户的状态和模式。

数据：
- 对话次数：{data.get('chat_count', 0)}
- 情绪分布：{json.dumps(data.get('emotion_distribution', {}), ensure_ascii=False)}
- 主导情绪：{data.get('dominant_emotion', 'neutral')}
- 新增记忆：{data.get('new_memory_count', 0)}
- 近期消息摘要：{'; '.join(data.get('recent_messages', [])[:10])}

请返回 JSON 格式：
{{
  "title": "洞察标题",
  "content": "洞察内容（100-300字，温暖的观察）",
  "summary": "一句话总结",
  "category": "emotion_pattern/behavior_pattern/growth_observation/relationship_observation/life_observation",
  "observations": ["观察1", "观察2", "观察3"],
  "evidence": {{"key": "value"}},
  "confidence": 0.7
}}

只返回 JSON。"""
        
        result = await llm_service.analysis(
            prompt=prompt,
            system_message="你是生活洞察专家，善于从数据中观察用户的生活模式和情绪状态。只返回 JSON。"
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
    
    def _generate_with_rules(self, insight_type: str, data: Dict) -> Dict[str, Any]:
        """规则生成洞察（后备）"""
        dominant = data.get("dominant_emotion", "neutral")
        chat_count = data.get("chat_count", 0)
        
        emotion_names = {
            "happy": "开心", "sad": "低落", "anxious": "焦虑",
            "angry": "生气", "lonely": "孤独", "neutral": "平稳",
        }
        emotion_name = emotion_names.get(dominant, "平稳")
        
        period = "这周" if insight_type == "weekly" else "这个月"
        
        observations = [f"情绪以{emotion_name}为主"]
        if chat_count > 20:
            observations.append("交流比较活跃")
        elif chat_count < 5:
            observations.append("交流比较少")
        
        content = f"{period}，你的情绪整体偏{emotion_name}。"
        if chat_count > 0:
            content += f"我们聊了{chat_count}次，"
        content += "希望接下来的日子也好好照顾自己。"
        
        return {
            "title": f"{period}的心情观察",
            "content": content,
            "summary": f"情绪偏{emotion_name}",
            "category": "emotion_pattern",
            "observations": observations,
            "evidence": data.get("emotion_distribution", {}),
            "confidence": 0.5,
        }
    
    async def get_insights(
        self,
        user_id: str,
        insight_type: Optional[str] = None,
        limit: int = 10,
        db=None,
    ) -> List[Dict[str, Any]]:
        """获取洞察列表"""
        from models.insight import Insight
        from sqlalchemy import select, desc, and_
        
        conditions = [Insight.user_id == user_id, Insight.is_active == True]
        if insight_type:
            conditions.append(Insight.insight_type == insight_type)
        
        stmt = select(Insight).where(
            and_(*conditions)
        ).order_by(desc(Insight.created_at)).limit(limit)
        
        result = await db.execute(stmt)
        insights = result.scalars().all()
        
        return [
            {
                "id": i.id,
                "insight_type": i.insight_type,
                "title": i.title,
                "content": i.content,
                "summary": i.summary,
                "category": i.category,
                "confidence": i.confidence,
                "period_start": i.period_start.isoformat(),
                "period_end": i.period_end.isoformat(),
                "created_at": i.created_at.isoformat(),
            }
            for i in insights
        ]


# 全局实例
insight_engine = InsightEngine()
