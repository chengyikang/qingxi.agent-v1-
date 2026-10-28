"""
Module 04: Life Memory Engine
Memory 重新设计为6层（Identity/Preference/Relationship/Life Event/Emotion/Growth）
支持新增/修改/删除/引用/时间轴关联/可信度更新
Memory 不是聊天记录，Memory 是人生
"""
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class LifeMemoryEngine:
    """人生记忆引擎 - 6 层记忆系统"""
    
    # 6 层定义
    LAYERS = {
        "identity": {
            "name": "身份层",
            "description": "核心身份信息：名字、年龄、职业、教育等",
            "categories": ["identity", "education", "career"],
            "default_confidence": 0.9,
        },
        "preference": {
            "name": "偏好层",
            "description": "喜好和习惯：兴趣、偏好、风格",
            "categories": ["interest", "preference"],
            "default_confidence": 0.7,
        },
        "relationship": {
            "name": "关系层",
            "description": "与他人的关系：家人、朋友、同事",
            "categories": ["relationship", "important_person"],
            "default_confidence": 0.8,
        },
        "life_event": {
            "name": "事件层",
            "description": "重要人生事件：转折、成就、挑战",
            "categories": ["important_event", "milestone", "challenge"],
            "default_confidence": 0.8,
        },
        "emotion": {
            "name": "情绪层",
            "description": "情绪模式和特点：情绪倾向、触发条件",
            "categories": ["emotion_pattern", "emotion_tendency"],
            "default_confidence": 0.6,
        },
        "growth": {
            "name": "成长层",
            "description": "成长经历和感悟：学到的、改变的",
            "categories": ["growth", "learning", "insight"],
            "default_confidence": 0.7,
        },
    }
    
    # 旧 category 到新 layer 的映射（兼容 V0）
    CATEGORY_TO_LAYER = {
        "interest": "preference",
        "education": "identity",
        "career": "identity",
        "dream": "preference",
        "problem": "emotion",
        "preference": "preference",
        "important_event": "life_event",
    }
    
    def __init__(self):
        self.max_memories_per_extraction = 5
        self.retrieval_limit = 10
    
    def get_layer_for_category(self, category: str) -> str:
        """根据 category 确定 layer"""
        return self.CATEGORY_TO_LAYER.get(category, "identity")
    
    def get_default_confidence(self, layer: str) -> float:
        """获取层的默认可信度"""
        layer_config = self.LAYERS.get(layer, {})
        return layer_config.get("default_confidence", 0.7)
    
    async def create_memory(
        self,
        user_id: str,
        content: str,
        category: str,
        layer: Optional[str] = None,
        importance: int = 5,
        source: str = "chat",
        confidence: Optional[float] = None,
        event_time: Optional[datetime] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        db=None,
    ) -> Optional[str]:
        """创建记忆（V1 增强）"""
        from models.memory import Memory
        
        # 自动确定 layer
        if not layer:
            layer = self.get_layer_for_category(category)
        
        # 自动确定 confidence
        if confidence is None:
            confidence = self.get_default_confidence(layer)
        
        memory_id = str(uuid.uuid4())
        
        memory = Memory(
            id=memory_id,
            user_id=user_id,
            content=content,
            category=category,
            importance=min(max(importance, 1), 10),
            layer=layer,
            source=source,
            confidence=confidence,
            event_time=event_time,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            is_active=True,
            version=1,
        )
        db.add(memory)
        await db.flush()
        
        # 同步到向量存储
        try:
            from memory.vector_store import vector_store
            vector_store.add_memory(
                user_id=user_id,
                memory_id=memory_id,
                content=content,
                category=category,
                importance=importance,
            )
        except Exception as e:
            logger.warning(f"向量存储同步失败: {e}")
        
        return memory_id
    
    async def update_memory(
        self,
        memory_id: str,
        user_id: str,
        new_content: Optional[str] = None,
        new_confidence: Optional[float] = None,
        new_importance: Optional[int] = None,
        db=None,
    ) -> bool:
        """更新记忆（版本递增）"""
        from models.memory import Memory
        from sqlalchemy import select
        
        stmt = select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == user_id,
            Memory.is_active == True
        )
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if not memory:
            return False
        
        if new_content is not None:
            memory.content = new_content
        if new_confidence is not None:
            memory.confidence = min(max(new_confidence, 0.0), 1.0)
        if new_importance is not None:
            memory.importance = min(max(new_importance, 1), 10)
        
        memory.version += 1
        memory.updated_at = datetime.utcnow()
        
        return True
    
    async def delete_memory(self, memory_id: str, user_id: str, db=None) -> bool:
        """软删除记忆"""
        from models.memory import Memory
        from sqlalchemy import select
        
        stmt = select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == user_id
        )
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()
        
        if memory:
            memory.is_active = False
            return True
        return False
    
    async def retrieve_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
        layer: Optional[str] = None,
        category: Optional[str] = None,
        min_confidence: float = 0.0,
        db=None,
    ) -> List[Dict[str, Any]]:
        """检索记忆（V1 增强：支持层级过滤、可信度过滤）"""
        from models.memory import Memory
        from sqlalchemy import select, desc, and_
        
        # 构建查询条件
        conditions = [
            Memory.user_id == user_id,
            Memory.is_active == True,
            Memory.confidence >= min_confidence,
        ]
        if layer:
            conditions.append(Memory.layer == layer)
        if category:
            conditions.append(Memory.category == category)
        
        stmt = select(Memory).where(
            and_(*conditions)
        ).order_by(
            desc(Memory.importance), desc(Memory.confidence), desc(Memory.created_at)
        ).limit(limit)
        
        result = await db.execute(stmt)
        memories = result.scalars().all()
        
        return [
            {
                "id": m.id,
                "content": m.content,
                "category": m.category,
                "layer": m.layer,
                "importance": m.importance,
                "confidence": m.confidence,
                "source": m.source,
                "event_time": m.event_time.isoformat() if m.event_time else None,
                "created_at": m.created_at.isoformat(),
            }
            for m in memories
        ]
    
    async def retrieve_by_layer(
        self,
        user_id: str,
        layer: str,
        limit: int = 20,
        db=None,
    ) -> List[Dict[str, Any]]:
        """按层级检索记忆"""
        return await self.retrieve_memories(
            user_id=user_id, query="", limit=limit, layer=layer, db=db
        )
    
    async def get_memory_statistics(self, user_id: str, db=None) -> Dict[str, Any]:
        """获取记忆统计"""
        from models.memory import Memory
        from sqlalchemy import select, func, and_
        
        # 总数
        total_stmt = select(func.count(Memory.id)).where(
            Memory.user_id == user_id, Memory.is_active == True
        )
        total = (await db.execute(total_stmt)).scalar() or 0
        
        # 按层级统计
        layer_stats = {}
        for layer_key, layer_config in self.LAYERS.items():
            stmt = select(func.count(Memory.id)).where(
                Memory.user_id == user_id,
                Memory.is_active == True,
                Memory.layer == layer_key
            )
            count = (await db.execute(stmt)).scalar() or 0
            layer_stats[layer_key] = {
                "name": layer_config["name"],
                "count": count,
            }
        
        # 按来源统计
        source_stats = {}
        for source in ["chat", "import", "persona", "insight", "reflection", "system"]:
            stmt = select(func.count(Memory.id)).where(
                Memory.user_id == user_id,
                Memory.is_active == True,
                Memory.source == source
            )
            count = (await db.execute(stmt)).scalar() or 0
            if count > 0:
                source_stats[source] = count
        
        # 平均可信度
        avg_conf_stmt = select(func.avg(Memory.confidence)).where(
            Memory.user_id == user_id, Memory.is_active == True
        )
        avg_confidence = (await db.execute(avg_conf_stmt)).scalar() or 0
        
        return {
            "total": total,
            "by_layer": layer_stats,
            "by_source": source_stats,
            "avg_confidence": round(avg_confidence, 2),
        }
    
    async def extract_memories_from_chat(
        self,
        conversation: str,
        user_id: str,
        db=None,
    ) -> List[str]:
        """从对话中提取记忆（V1 升级：6层分类）"""
        from services.llm import llm_service
        
        try:
            prompt = f"""你是一个记忆提取专家。请从对话中提取用户的重要信息。

对话内容:
{conversation}

请返回 JSON 格式的记忆列表，每条记忆包含:
- content: 记忆内容（简洁，30字以内）
- category: 类别，必须是以下之一:
  - identity: 身份信息
  - interest: 兴趣爱好
  - education: 教育背景
  - career: 职业工作
  - dream: 梦想愿望
  - problem: 烦恼问题
  - preference: 偏好习惯
  - important_event: 重要事件
  - emotion_pattern: 情绪模式
  - growth: 成长感悟
  - relationship: 人际关系
- importance: 重要性（1-10）
- layer: 记忆层级，必须是以下之一:
  - identity: 身份层
  - preference: 偏好层
  - relationship: 关系层
  - life_event: 事件层
  - emotion: 情绪层
  - growth: 成长层

如果没有提取到重要记忆，返回空数组 []。
只返回 JSON 数组。"""
            
            result = await llm_service.analysis(
                prompt=prompt,
                system_message="你是记忆提取专家，只返回 JSON 格式的记忆列表。"
            )
            
            if isinstance(result, str):
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                if result.startswith("```"):
                    result = result[3:]
                if result.endswith("```"):
                    result = result[:-3]
                result = json.loads(result.strip())
            
            if not result or not isinstance(result, list):
                return []
            
            # 保存记忆
            memory_ids = []
            for memory_data in result[:self.max_memories_per_extraction]:
                layer = memory_data.get("layer", self.get_layer_for_category(memory_data.get("category", "identity")))
                memory_id = await self.create_memory(
                    user_id=user_id,
                    content=memory_data.get("content", ""),
                    category=memory_data.get("category", "important_event"),
                    layer=layer,
                    importance=memory_data.get("importance", 5),
                    source="chat",
                    db=db,
                )
                if memory_id:
                    memory_ids.append(memory_id)
            
            return memory_ids
        except Exception as e:
            logger.error(f"提取记忆失败: {e}")
            return []
    
    def build_memory_prompt_section(self, memories: List[Dict[str, Any]]) -> str:
        """构建记忆相关的 Prompt 片段"""
        if not memories:
            return ""
        
        # 按层分组
        by_layer = {}
        for m in memories:
            layer = m.get("layer", "identity")
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(m)
        
        parts = ["【关于用户的记忆】"]
        
        for layer_key in ["identity", "preference", "relationship", "life_event", "emotion", "growth"]:
            if layer_key in by_layer:
                layer_name = self.LAYERS.get(layer_key, {}).get("name", layer_key)
                parts.append(f"\n{layer_name}：")
                for i, m in enumerate(by_layer[layer_key][:5], 1):
                    parts.append(f"  {i}. {m.get('content', '')}")
        
        return "\n".join(parts)


# 全局实例
life_memory_engine = LifeMemoryEngine()
