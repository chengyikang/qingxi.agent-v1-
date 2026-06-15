"""
聊天服务
核心聊天逻辑：调用 prompt builder、调用 LLM、保存历史
"""
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from models.chat import ChatHistory
from models.trust import TrustProfile
from models.personality import PersonalityState
from services.llm import llm_service
from services.trust import trust_service
from services.memory import memory_service
from services.emotion import emotion_service
from services.personality import personality_service
from prompt.builder import prompt_builder
from emotion.analyzer import emotion_analyzer


class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        """初始化聊天服务"""
        self.history_limit = 50  # 保留历史记录数
        self.memory_retrieval_limit = 5  # 检索记忆数量
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        处理用户消息，返回 Agent 回复
        
        完整流程：
        1. 保存用户消息
        2. 获取信任档案和人格状态
        3. 检索相关记忆
        4. 分析情绪
        5. 构建 Prompt
        6. 调用 LLM 获取回复
        7. 保存 Agent 回复
        8. 更新信任值
        9. 更新人格状态
        10. 提取并保存新记忆（定期）
        
        Args:
            user_id: 用户ID
            message: 用户消息
            db: 数据库会话
            
        Returns:
            处理结果
        """
        try:
            # 1. 保存用户消息
            user_chat = ChatHistory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                role="user",
                content=message
            )
            db.add(user_chat)
            await db.flush()
            
            # 2. 获取信任档案
            trust_profile = await trust_service.get_or_create_profile(user_id, db)
            relationship_stage = trust_profile.relationship_stage
            trust_score = trust_profile.trust_score
            
            # 3. 获取人格状态
            personality_state = await personality_service.get_or_create_state(user_id, db)
            personality_dict = {
                "openness": personality_state.openness,
                "initiative": personality_state.initiative,
                "vulnerability": personality_state.vulnerability
            }
            
            # 4. 检索相关记忆
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query=message,
                limit=self.memory_retrieval_limit
            )
            memory_context = memory_service.get_memory_context(memories)
            
            # 5. 分析情绪
            emotion_result = await emotion_service.analyze_and_log(user_id, message, db)
            emotion_hint = ""
            if emotion_result and emotion_result["confidence"] > 0.6:
                emotion_hint = emotion_analyzer.get_emotion_response_hint(emotion_result["emotion"])
            
            # 6. 获取最近对话历史
            recent_history = await self.get_recent_history(user_id, db, limit=20)
            history_dicts = [
                {"role": h.role, "content": h.content}
                for h in recent_history
            ]
            
            # 7. 构建 Prompt 并调用 LLM
            messages = prompt_builder.build_chat_prompt(
                user_message=message,
                relationship_stage=relationship_stage,
                trust_score=trust_score,
                personality_state=personality_dict,
                memory_context=memory_context,
                emotion_hint=emotion_hint,
                recent_history=history_dicts
            )
            
            response = await llm_service.chat_completion(
                messages=messages,
                temperature=0.8,
                max_tokens=1000
            )
            
            # 8. 保存 Agent 回复
            assistant_chat = ChatHistory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                role="assistant",
                content=response
            )
            db.add(assistant_chat)
            await db.flush()
            
            # 9. 更新信任值
            trust_update = await trust_service.update_trust(user_id, message, db)
            
            # 10. 更新人格状态
            personality_update = await personality_service.update_from_trust_growth(
                user_id,
                trust_update.get("growth", 0),
                db
            )
            
            # 定期提取记忆（基于对话长度或随机）
            new_memory_ids = []
            if len(history_dicts) % 5 == 0:  # 每5轮对话尝试提取记忆
                conversation_text = "\n".join([
                    f"{'用户' if h['role'] == 'user' else '清溪'}：{h['content']}"
                    for h in history_dicts[-10:]
                ])
                conversation_text += f"\n用户：{message}\n清溪：{response}"
                new_memory_ids = await memory_service.extract_memories(
                    conversation=conversation_text,
                    user_id=user_id,
                    db=db
                )
            
            # 更新用户最后活跃时间
            from models.user import User
            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            if user:
                user.last_active_at = datetime.utcnow()
            
            return {
                "user_message_id": user_chat.id,
                "assistant_message_id": assistant_chat.id,
                "response": response,
                "emotion": emotion_result,
                "trust_update": trust_update,
                "personality_update": personality_update,
                "new_memories": new_memory_ids,
                "context": {
                    "relationship_stage": relationship_stage,
                    "trust_score": trust_score,
                    "personality": personality_dict
                }
            }
        except Exception as e:
            print(f"处理消息失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "response": "抱歉，我现在有些问题，无法回复你。"
            }
    
    async def get_recent_history(
        self,
        user_id: str,
        db: AsyncSession,
        limit: int = 50
    ) -> List[ChatHistory]:
        """
        获取最近聊天历史
        
        Args:
            user_id: 用户ID
            db: 数据库会话
            limit: 限制数量
            
        Returns:
            聊天历史列表
        """
        try:
            stmt = select(ChatHistory).where(
                ChatHistory.user_id == user_id
            ).order_by(desc(ChatHistory.created_at)).limit(limit)
            
            result = await db.execute(stmt)
            histories = result.scalars().all()
            
            # 倒序返回（按时间正序）
            return list(reversed(histories))
        except Exception as e:
            print(f"获取聊天历史失败: {e}")
            return []
    
    async def get_history_dict(
        self,
        user_id: str,
        db: AsyncSession,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取聊天历史（字典格式）
        
        Args:
            user_id: 用户ID
            db: 数据库会话
            limit: 限制数量
            
        Returns:
            聊天历史字典列表
        """
        histories = await self.get_recent_history(user_id, db, limit)
        return [
            {
                "id": h.id,
                "role": h.role,
                "content": h.content,
                "created_at": h.created_at.isoformat()
            }
            for h in histories
        ]


# 全局聊天服务实例
chat_service = ChatService()
