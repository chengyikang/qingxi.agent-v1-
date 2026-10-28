"""聊天服务 V1 - 委托给 CompanionEngine"""
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from engines.companion.engine import companion_engine


class ChatService:
    """聊天服务 - V1 使用 CompanionEngine"""
    
    async def process_message(self, user_id: str, message: str, db: AsyncSession) -> Dict[str, Any]:
        return await companion_engine.process_message(user_id, message, db)
    
    async def get_recent_history(self, user_id, db, limit=50):
        from models.chat import ChatHistory
        from sqlalchemy import select, desc
        stmt = select(ChatHistory).where(ChatHistory.user_id == user_id).order_by(desc(ChatHistory.created_at)).limit(limit)
        result = await db.execute(stmt)
        return list(reversed(result.scalars().all()))
    
    async def get_history_dict(self, user_id, db, limit=50):
        histories = await self.get_recent_history(user_id, db, limit)
        return [{"id": h.id, "role": h.role, "content": h.content, "created_at": h.created_at.isoformat()} for h in histories]


chat_service = ChatService()
