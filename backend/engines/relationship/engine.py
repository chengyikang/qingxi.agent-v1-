"""
Module 05: Relationship Engine
保留 Trust 系统，新增 Relationship Context（共同经历记录）
Timeline 不是历史，Timeline 是共同经历
"""
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RelationshipEngine:
    """关系引擎"""
    
    # 关系里程碑触发条件
    MILESTONE_TRIGGERS = {
        "first_dream": {
            "keywords": ["梦想", "希望", "想成为", "理想", "未来想"],
            "title": "第一次聊梦想",
            "significance": 0.8,
        },
        "first_trouble": {
            "keywords": ["烦恼", "困扰", "难受", "压力", "困难"],
            "title": "第一次分享烦恼",
            "significance": 0.7,
        },
        "first_vulnerability": {
            "keywords": ["害怕", "孤独", "想哭", "崩溃", "撑不住"],
            "title": "第一次表露脆弱",
            "significance": 0.9,
        },
        "first_gratitude": {
            "keywords": ["谢谢", "感谢", "多亏", "你真好", "感恩"],
            "title": "第一次表达感谢",
            "significance": 0.6,
        },
        "first_deep_conversation": {
            "keywords": ["人生", "意义", "价值", "思考", "为什么"],
            "title": "第一次深入对话",
            "significance": 0.7,
        },
    }
    
    # 信任阶段转换里程碑
    STAGE_MILESTONES = {
        ("stranger", "familiar"): "从陌生到熟悉",
        ("familiar", "friend"): "从熟悉到朋友",
        ("friend", "close_friend"): "从朋友到知己",
    }
    
    async def check_and_record_milestones(
        self,
        user_id: str,
        message: str,
        emotion: str,
        trust_score: int,
        old_stage: str,
        new_stage: str,
        db,
    ) -> List[Dict[str, Any]]:
        """检查并记录关系里程碑"""
        from models.relationship_context import RelationshipContext
        from sqlalchemy import select
        
        milestones_created = []
        
        # 1. 检查第一次类型的里程碑
        for trigger_type, trigger_config in self.MILESTONE_TRIGGERS.items():
            # 检查是否已存在
            stmt = select(RelationshipContext).where(
                RelationshipContext.user_id == user_id,
                RelationshipContext.context_type == trigger_type,
                RelationshipContext.is_active == True,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                continue  # 已经记录过了
            
            # 检查是否触发
            message_lower = message.lower()
            triggered = any(kw in message_lower for kw in trigger_config["keywords"])
            
            if triggered:
                rc = RelationshipContext(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    context_type=trigger_type,
                    title=trigger_config["title"],
                    chat_summary=message[:200],
                    occurred_at=datetime.utcnow(),
                    emotion_at=emotion,
                    significance=trigger_config["significance"],
                    is_milestone=True,
                )
                db.add(rc)
                await db.flush()
                
                milestones_created.append({
                    "type": trigger_type,
                    "title": trigger_config["title"],
                    "significance": trigger_config["significance"],
                })
        
        # 2. 检查信任阶段转换
        if old_stage != new_stage:
            stage_key = (old_stage, new_stage)
            if stage_key in self.STAGE_MILESTONES:
                rc = RelationshipContext(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    context_type="trust_milestone",
                    title=self.STAGE_MILESTONES[stage_key],
                    chat_summary=f"信任值达到 {trust_score}，关系从{old_stage}变为{new_stage}",
                    occurred_at=datetime.utcnow(),
                    significance=0.9,
                    is_milestone=True,
                    milestone_type=f"{old_stage}_to_{new_stage}",
                )
                db.add(rc)
                await db.flush()
                
                milestones_created.append({
                    "type": "trust_milestone",
                    "title": self.STAGE_MILESTONES[stage_key],
                    "significance": 0.9,
                })
        
        return milestones_created
    
    async def get_relationship_context(
        self,
        user_id: str,
        db,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """获取关系上下文"""
        from models.relationship_context import RelationshipContext
        from sqlalchemy import select, desc
        
        stmt = select(RelationshipContext).where(
            RelationshipContext.user_id == user_id,
            RelationshipContext.is_active == True,
        ).order_by(
            desc(RelationshipContext.significance),
            desc(RelationshipContext.occurred_at),
        ).limit(limit)
        
        result = await db.execute(stmt)
        contexts = result.scalars().all()
        
        return [
            {
                "id": c.id,
                "context_type": c.context_type,
                "title": c.title,
                "description": c.description,
                "occurred_at": c.occurred_at.isoformat(),
                "emotion_at": c.emotion_at,
                "significance": c.significance,
                "is_milestone": c.is_milestone,
            }
            for c in contexts
        ]
    
    def build_relationship_prompt_section(
        self,
        relationship_contexts: List[Dict[str, Any]],
        trust_score: int,
        relationship_stage: str,
    ) -> str:
        """构建关系相关的 Prompt 片段"""
        stage_labels = {
            "stranger": "陌生",
            "familiar": "熟悉",
            "friend": "朋友",
            "close_friend": "知己",
        }
        
        parts = [f"【关系状态】"]
        parts.append(f"信任值：{trust_score}/1000")
        parts.append(f"关系阶段：{stage_labels.get(relationship_stage, relationship_stage)}")
        
        if relationship_contexts:
            parts.append(f"\n【共同经历】")
            for ctx in relationship_contexts[:5]:
                marker = "⭐" if ctx.get("is_milestone") else "·"
                parts.append(f"  {marker} {ctx.get('title', '')}")
        
        return "\n".join(parts)


# 全局实例
relationship_engine = RelationshipEngine()
