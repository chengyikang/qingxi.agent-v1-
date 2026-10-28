"""记忆服务 V1 - 委托给 LifeMemoryEngine"""
import uuid
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from models.memory import Memory
from memory.vector_store import vector_store
from engines.life_memory.engine import life_memory_engine


class MemoryService:
    """记忆服务 - V1 使用 LifeMemoryEngine"""
    
    async def extract_memories(self, conversation, user_id, db):
        return await life_memory_engine.extract_memories_from_chat(conversation, user_id, db)
    
    async def create_memory(self, user_id, content, category, importance, db, layer=None, source="chat"):
        return await life_memory_engine.create_memory(
            user_id=user_id, content=content, category=category,
            importance=importance, layer=layer, source=source, db=db
        )
    
    async def retrieve_memories(self, user_id, query, limit=5, category=None):
        return vector_store.search_memories(user_id=user_id, query=query, n_results=limit, category=category)
    
    async def get_user_memories(self, user_id, db, limit=50):
        stmt = select(Memory).where(Memory.user_id == user_id, Memory.is_active == True).order_by(desc(Memory.importance), desc(Memory.created_at)).limit(limit)
        result = await db.execute(stmt)
        return [{"id": m.id, "content": m.content, "category": m.category, "layer": m.layer, "importance": m.importance, "confidence": m.confidence, "created_at": m.created_at.isoformat()} for m in result.scalars().all()]
    
    async def delete_memory(self, user_id, memory_id, db):
        return await life_memory_engine.delete_memory(memory_id, user_id, db)
    
    def get_memory_context(self, memories):
        if not memories: return ""
        context_parts = ["关于用户的重要信息："]
        category_names = {"interest": "兴趣", "education": "教育", "career": "职业", "dream": "梦想", "problem": "烦恼", "preference": "偏好", "important_event": "重要事件"}
        for i, m in enumerate(memories, 1):
            cat = category_names.get(m.get("category", ""), m.get("category", ""))
            context_parts.append(f"{i}. [{cat}]{m.get('content', '')}")
        return "\n".join(context_parts)


memory_service = MemoryService()
