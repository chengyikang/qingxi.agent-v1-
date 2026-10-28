"""
Module 06: Companion Engine
产品大脑，协调所有模块
聊天流程：用户输入 → Emotion Analysis → Persona Retrieval → Memory Retrieval
         → Relationship Retrieval → Timeline Retrieval → Prompt Builder → LLM
聊天不是核心，理解用户才是核心
"""
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CompanionEngine:
    """陪伴引擎 - 协调所有模块"""
    
    def __init__(self):
        self.history_limit = 20
        self.memory_retrieval_limit = 10
        self.memory_extraction_interval = 5  # 每 N 轮提取记忆
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        db,
    ) -> Dict[str, Any]:
        """
        处理用户消息 - 完整的 V1 流程
        
        流程：
        1. 保存用户消息
        2. Emotion Analysis → 情绪分析
        3. Persona Retrieval → 获取用户人格
        4. Memory Retrieval → 检索相关记忆
        5. Relationship Retrieval → 获取关系上下文
        6. Timeline Retrieval → 获取时间轴
        7. Insight Retrieval → 获取近期洞察
        8. Prompt Builder → 构建完整 Prompt
        9. LLM → 生成回复
        10. 保存回复
        11. 更新信任值
        12. 更新人格
        13. 检查关系里程碑
        14. 提取记忆（定期）
        15. 更新时间轴
        """
        try:
            # === Step 1: 保存用户消息 ===
            user_chat = await self._save_user_message(user_id, message, db)
            
            # === Step 2: Emotion Analysis ===
            emotion_result = await self._analyze_emotion(user_id, message, db)
            
            # === Step 3: Persona Retrieval ===
            persona_data = await self._get_persona(user_id, db)
            
            # === Step 4: Memory Retrieval ===
            memories = await self._retrieve_memories(user_id, message, db)
            
            # === Step 5: Relationship Retrieval ===
            trust_profile, relationship_contexts = await self._get_relationship(user_id, db)
            
            # === Step 6: Timeline Retrieval ===
            timeline_entries = await self._get_timeline(user_id, db)
            
            # === Step 7: Insight Retrieval ===
            recent_insights = await self._get_recent_insights(user_id, db)
            
            # === Step 8: Get Recent History ===
            recent_history = await self._get_recent_history(user_id, db)
            
            # === Step 9: Prompt Builder + LLM ===
            response = await self._generate_response(
                message=message,
                emotion=emotion_result,
                persona=persona_data,
                memories=memories,
                trust_profile=trust_profile,
                relationship_contexts=relationship_contexts,
                timeline_entries=timeline_entries,
                recent_insights=recent_insights,
                recent_history=recent_history,
            )
            
            # === Step 10: 保存回复 ===
            assistant_chat = await self._save_assistant_message(
                user_id, response, emotion_result, trust_profile, db
            )
            
            # === Step 11: 更新信任值 ===
            trust_update = await self._update_trust(user_id, message, db)
            
            # === Step 12: 更新人格 ===
            persona_update = await self._update_persona(
                user_id, message, response, emotion_result, trust_profile, db
            )
            
            # === Step 13: 检查关系里程碑 ===
            milestones = await self._check_milestones(
                user_id, message, emotion_result, trust_update, db
            )
            
            # === Step 14: 提取记忆 ===
            new_memory_ids = []
            if len(recent_history) % self.memory_extraction_interval == 0:
                new_memory_ids = await self._extract_memories(
                    user_id, message, response, recent_history, db
                )
            
            # === Step 15: 更新时间轴 ===
            await self._update_timeline(user_id, message, emotion_result, db)
            
            # 更新用户活跃时间
            await self._update_user_activity(user_id, db)
            
            # 组装返回结果
            return {
                "user_message_id": user_chat.id,
                "assistant_message_id": assistant_chat.id,
                "response": response,
                "emotion": emotion_result,
                "trust_update": trust_update,
                "persona_update": persona_update,
                "milestones": milestones,
                "new_memories": new_memory_ids,
                "context": {
                    "relationship_stage": trust_profile.relationship_stage if trust_profile else "stranger",
                    "trust_score": trust_profile.trust_score if trust_profile else 10,
                    "persona_maturity": persona_data.get("maturity_score", 0) if persona_data else 0,
                    "memory_count": len(memories),
                    "milestone_count": len(relationship_contexts),
                }
            }
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "response": "抱歉，我现在有些问题，无法回复你。",
            }
    
    async def _save_user_message(self, user_id: str, message: str, db):
        """保存用户消息"""
        from models.chat import ChatHistory
        chat = ChatHistory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            role="user",
            content=message,
        )
        db.add(chat)
        await db.flush()
        return chat
    
    async def _analyze_emotion(self, user_id: str, message: str, db) -> Dict[str, Any]:
        """情绪分析"""
        from services.emotion import emotion_service
        return await emotion_service.analyze_and_log(user_id, message, db) or {}
    
    async def _get_persona(self, user_id: str, db) -> Dict[str, Any]:
        """获取用户人格"""
        from models.persona import Persona
        from sqlalchemy import select
        stmt = select(Persona).where(Persona.user_id == user_id)
        result = await db.execute(stmt)
        persona = result.scalar_one_or_none()
        if persona:
            return persona.to_prompt_dict()
        return {}
    
    async def _retrieve_memories(self, user_id: str, message: str, db) -> List[Dict]:
        """检索相关记忆"""
        from engines.life_memory.engine import life_memory_engine
        return await life_memory_engine.retrieve_memories(
            user_id=user_id, query=message, limit=self.memory_retrieval_limit, db=db
        )
    
    async def _get_relationship(self, user_id: str, db):
        """获取关系信息"""
        from models.trust import TrustProfile
        from services.trust import trust_service
        from engines.relationship.engine import relationship_engine
        
        trust_profile = await trust_service.get_or_create_profile(user_id, db)
        contexts = await relationship_engine.get_relationship_context(user_id, db)
        return trust_profile, contexts
    
    async def _get_timeline(self, user_id: str, db) -> List[Dict]:
        """获取时间轴"""
        from models.timeline import Timeline
        from sqlalchemy import select, desc
        stmt = select(Timeline).where(
            Timeline.user_id == user_id,
            Timeline.is_active == True,
        ).order_by(desc(Timeline.occurred_at)).limit(10)
        result = await db.execute(stmt)
        entries = result.scalars().all()
        return [
            {
                "title": e.title,
                "entry_type": e.entry_type,
                "occurred_at": e.occurred_at.isoformat(),
                "emotion_marker": e.emotion_marker,
                "is_shared": e.is_shared_with_companion,
            }
            for e in entries
        ]
    
    async def _get_recent_insights(self, user_id: str, db) -> List[Dict]:
        """获取近期洞察"""
        from models.insight import Insight
        from sqlalchemy import select, desc
        stmt = select(Insight).where(
            Insight.user_id == user_id,
            Insight.is_active == True,
        ).order_by(desc(Insight.created_at)).limit(3)
        result = await db.execute(stmt)
        insights = result.scalars().all()
        return [
            {"title": i.title, "summary": i.summary, "category": i.category}
            for i in insights
        ]
    
    async def _get_recent_history(self, user_id: str, db) -> List[Dict]:
        """获取最近对话历史"""
        from models.chat import ChatHistory
        from sqlalchemy import select, desc
        stmt = select(ChatHistory).where(
            ChatHistory.user_id == user_id
        ).order_by(desc(ChatHistory.created_at)).limit(self.history_limit)
        result = await db.execute(stmt)
        histories = list(reversed(result.scalars().all()))
        return [{"role": h.role, "content": h.content} for h in histories]
    
    async def _generate_response(
        self,
        message: str,
        emotion: Dict,
        persona: Dict,
        memories: List[Dict],
        trust_profile,
        relationship_contexts: List[Dict],
        timeline_entries: List[Dict],
        recent_insights: List[Dict],
        recent_history: List[Dict],
    ) -> str:
        """构建 Prompt 并调用 LLM"""
        from prompt.builder import prompt_builder
        from services.llm import llm_service
        
        relationship_stage = trust_profile.relationship_stage if trust_profile else "stranger"
        trust_score = trust_profile.trust_score if trust_profile else 10
        
        # 构建完整 Prompt
        messages = prompt_builder.build_chat_prompt_v1(
            user_message=message,
            relationship_stage=relationship_stage,
            trust_score=trust_score,
            persona_data=persona,
            memories=memories,
            relationship_contexts=relationship_contexts,
            timeline_entries=timeline_entries,
            recent_insights=recent_insights,
            emotion=emotion,
            recent_history=recent_history,
        )
        
        return await llm_service.chat_completion(
            messages=messages, temperature=0.8, max_tokens=1000
        )
    
    async def _save_assistant_message(self, user_id, response, emotion, trust_profile, db):
        """保存助手消息"""
        from models.chat import ChatHistory
        chat = ChatHistory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            role="assistant",
            content=response,
            emotion_type=emotion.get("emotion") if emotion else None,
            emotion_confidence=emotion.get("confidence") if emotion else None,
            trust_score_at=trust_profile.trust_score if trust_profile else None,
        )
        db.add(chat)
        await db.flush()
        return chat
    
    async def _update_trust(self, user_id, message, db):
        """更新信任值"""
        from services.trust import trust_service
        return await trust_service.update_trust(user_id, message, db)
    
    async def _update_persona(self, user_id, message, response, emotion, trust_profile, db):
        """更新人格"""
        from engines.persona.engine import persona_engine
        emotion_type = emotion.get("emotion", "neutral") if emotion else "neutral"
        trust_score = trust_profile.trust_score if trust_profile else 10
        return await persona_engine.update_from_chat(
            user_id, message, response, emotion_type, trust_score, db
        )
    
    async def _check_milestones(self, user_id, message, emotion, trust_update, db):
        """检查关系里程碑"""
        from engines.relationship.engine import relationship_engine
        emotion_type = emotion.get("emotion", "neutral") if emotion else "neutral"
        old_stage = trust_update.get("old_stage", "stranger") if trust_update else "stranger"
        new_stage = trust_update.get("new_stage", "stranger") if trust_update else "stranger"
        trust_score = trust_update.get("new_trust", 10) if trust_update else 10
        return await relationship_engine.check_and_record_milestones(
            user_id, message, emotion_type, trust_score, old_stage, new_stage, db
        )
    
    async def _extract_memories(self, user_id, message, response, recent_history, db):
        """提取记忆"""
        from engines.life_memory.engine import life_memory_engine
        conversation_parts = [f"{'用户' if h['role'] == 'user' else '清溪'}：{h['content']}" for h in recent_history[-10:]]
        conversation_parts.append(f"用户：{message}")
        conversation_parts.append(f"清溪：{response}")
        conversation = "\n".join(conversation_parts)
        return await life_memory_engine.extract_memories_from_chat(
            conversation=conversation, user_id=user_id, db=db
        )
    
    async def _update_timeline(self, user_id, message, emotion, db):
        """更新时间轴"""
        from models.timeline import Timeline
        # 每次对话记录一条时间轴条目（如果重要的话）
        # 简单判断：如果情绪强度高或消息较长，记录为对话里程碑
        emotion_type = emotion.get("emotion", "neutral") if emotion else "neutral"
        confidence = emotion.get("confidence", 0) if emotion else 0
        
        if confidence > 0.7 and emotion_type != "neutral":
            entry = Timeline(
                id=str(uuid.uuid4()),
                user_id=user_id,
                entry_type="conversation_milestone",
                title=f"一次{emotion_type}的对话",
                description=message[:100],
                occurred_at=datetime.utcnow(),
                importance=6 if confidence > 0.8 else 4,
                is_shared_with_companion=True,
                emotion_marker=emotion_type,
            )
            db.add(entry)
            await db.flush()
    
    async def _update_user_activity(self, user_id, db):
        """更新用户活跃时间"""
        from models.user import User
        from sqlalchemy import select
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.last_active_at = datetime.utcnow()


# 全局实例
companion_engine = CompanionEngine()
