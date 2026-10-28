"""
Module 03: Persona Engine
建立用户数字人格（Identity、Communication Style、Thinking Style、
Emotion Style、Values、Preferences、Current Goals），持续成长更新
Persona 不是标签，Persona 是持续成长的人格
"""
import json
import logging
import math
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PersonaEngine:
    """数字人格引擎"""
    
    def __init__(self):
        self.growth_rate = 0.05  # 每次更新的增长率
        self.max_dimension = 1.0
        self.min_dimension = 0.0
    
    async def create_initial_persona(self, user_id: str, db) -> Dict[str, Any]:
        """创建初始人格"""
        from models.persona import Persona
        
        persona = Persona(
            user_id=user_id,
            identity_summary="暂未了解",
            identity_traits=[],
            identity_roles=[],
            comm_formality=0.5,
            comm_expressiveness=0.5,
            comm_directness=0.5,
            comm_humor=0.3,
            thinking_analytical=0.5,
            thinking_creative=0.5,
            thinking_practical=0.5,
            thinking_reflective=0.5,
            emotion_stability=0.5,
            emotion_expressiveness=0.5,
            emotion_sensitivity=0.5,
            emotion_optimism=0.5,
            maturity_score=0.0,
            growth_history=[],
            current_goals=[],
        )
        db.add(persona)
        await db.flush()
        return persona.to_prompt_dict()
    
    async def update_from_chat(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        emotion: str,
        trust_score: int,
        db,
    ) -> Dict[str, Any]:
        """从对话中更新人格"""
        from models.persona import Persona
        from sqlalchemy import select
        
        stmt = select(Persona).where(Persona.user_id == user_id)
        result = await db.execute(stmt)
        persona = result.scalar_one_or_none()
        
        if not persona:
            await self.create_initial_persona(user_id, db)
            result = await db.execute(stmt)
            persona = result.scalar_one_or_none()
        
        if not persona:
            return {}
        
        # 基于规则的渐进式更新（快速路径）
        updates = self._calculate_chat_updates(
            user_message, emotion, trust_score, persona
        )
        
        # 应用更新
        for key, value in updates.items():
            if hasattr(persona, key):
                current = getattr(persona, key)
                if isinstance(current, float):
                    setattr(persona, key, self._clamp(current + value))
        
        # 更新元数据
        persona.update_count += 1
        persona.last_updated_from = "chat"
        persona.maturity_score = min(
            persona.maturity_score + self.growth_rate * 0.1, 1.0
        )
        
        # 定期用 LLM 深度更新（每 20 次对话）
        if persona.update_count % 20 == 0:
            try:
                await self._deep_update_with_llm(user_id, persona, db)
            except Exception as e:
                logger.warning(f"LLM 深度更新人格失败: {e}")
        
        return persona.to_prompt_dict()
    
    def _calculate_chat_updates(
        self,
        message: str,
        emotion: str,
        trust_score: int,
        persona,
    ) -> Dict[str, float]:
        """基于对话计算人格维度更新"""
        updates = {}
        msg_len = len(message)
        
        # 消息越长，表达性越高
        if msg_len > 100:
            updates["comm_expressiveness"] = 0.01
        if msg_len > 300:
            updates["comm_expressiveness"] = 0.02
        
        # 情绪影响
        if emotion in ["sad", "anxious", "angry"]:
            updates["emotion_sensitivity"] = 0.005
            updates["emotion_stability"] = -0.002
        elif emotion in ["happy"]:
            updates["emotion_optimism"] = 0.005
            updates["emotion_stability"] = 0.002
        
        # 信任影响表达
        if trust_score > 300:
            updates["comm_directness"] = 0.005
        if trust_score > 600:
            updates["comm_formality"] = -0.005  # 更随意
        
        # 问问题多 → 分析型思维
        if "？" in message or "?" in message:
            updates["thinking_analytical"] = 0.003
        
        # 分享经历 → 反思型
        for kw in ["我曾经", "那时候", "以前", "记得"]:
            if kw in message:
                updates["thinking_reflective"] = 0.005
                break
        
        return updates
    
    async def _deep_update_with_llm(self, user_id: str, persona, db) -> None:
        """LLM 深度更新人格（定期调用）"""
        from services.llm import llm_service
        
        # 收集近期对话作为分析素材
        from models.chat import ChatHistory
        from sqlalchemy import select, desc
        stmt = select(ChatHistory).where(
            ChatHistory.user_id == user_id,
            ChatHistory.role == "user"
        ).order_by(desc(ChatHistory.created_at)).limit(30)
        result = await db.execute(stmt)
        recent_chats = result.scalars().all()
        
        if not recent_chats:
            return
        
        chat_text = "\n".join([f"用户: {c.content}" for c in recent_chats])
        
        prompt = f"""基于用户的近期对话，分析用户的人格特征。

近期对话：
{chat_text[:3000]}

当前人格数据：
{json.dumps(persona.to_prompt_dict(), ensure_ascii=False, indent=2)}

请分析并返回需要更新的维度，格式：
{{
  "identity_summary": "一句话身份概括",
  "identity_traits": ["特质1", "特质2"],
  "comm_formality_delta": 0.0,
  "comm_expressiveness_delta": 0.0,
  "thinking_analytical_delta": 0.0,
  "thinking_creative_delta": 0.0,
  "emotion_stability_delta": 0.0,
  "emotion_optimism_delta": 0.0,
  "values_core": [{{"value": "价值观", "importance": 0.8}}],
  "current_goals": [{{"goal": "目标", "status": "active", "progress": 0.3}}]
}}

delta 范围: -0.1 到 0.1。只返回 JSON。"""
        
        result_str = await llm_service.analysis(
            prompt=prompt,
            system_message="你是一个人格分析专家，根据对话分析用户的人格特征变化。只返回 JSON。"
        )
        
        if isinstance(result_str, str):
            result_str = result_str.strip()
            if result_str.startswith("```json"):
                result_str = result_str[7:]
            if result_str.startswith("```"):
                result_str = result_str[3:]
            if result_str.endswith("```"):
                result_str = result_str[:-3]
            updates = json.loads(result_str.strip())
        else:
            updates = result_str
        
        # 应用更新
        if "identity_summary" in updates and updates["identity_summary"]:
            persona.identity_summary = updates["identity_summary"]
        if "identity_traits" in updates and updates["identity_traits"]:
            persona.identity_traits = updates["identity_traits"]
        if "values_core" in updates and updates["values_core"]:
            persona.values_core = updates["values_core"]
        if "current_goals" in updates and updates["current_goals"]:
            persona.current_goals = updates["current_goals"]
        
        # 应用 delta 更新
        delta_fields = [
            "comm_formality", "comm_expressiveness", "thinking_analytical",
            "thinking_creative", "emotion_stability", "emotion_optimism"
        ]
        for field in delta_fields:
            delta_key = f"{field}_delta"
            if delta_key in updates:
                delta = float(updates[delta_key])
                current = getattr(persona, field)
                setattr(persona, field, self._clamp(current + delta))
    
    async def update_from_import(
        self,
        user_id: str,
        parsed_data: Dict[str, Any],
        db,
    ) -> Dict[str, Any]:
        """从导入数据更新人格"""
        from models.persona import Persona
        from sqlalchemy import select
        
        stmt = select(Persona).where(Persona.user_id == user_id)
        result = await db.execute(stmt)
        persona = result.scalar_one_or_none()
        
        if not persona:
            return {}
        
        # 从解析数据中提取人格信息
        if parsed_data.get("interests"):
            existing = persona.preferences_topics or []
            new_topics = [i.get("name", "") for i in parsed_data["interests"] if i.get("name")]
            persona.preferences_topics = list(set(existing + new_topics))
        
        if parsed_data.get("goals"):
            existing = persona.current_goals or []
            new_goals = [
                {"goal": g.get("goal", ""), "status": g.get("status", "active"), "progress": 0.0}
                for g in parsed_data["goals"] if g.get("goal")
            ]
            persona.current_goals = existing + new_goals
        
        if parsed_data.get("values"):
            persona.values_core = parsed_data["values"]
        
        if parsed_data.get("emotions"):
            persona.emotion_patterns = parsed_data["emotions"]
        
        if parsed_data.get("people"):
            persona.identity_roles = list(set(
                (persona.identity_roles or []) +
                [p.get("relation", "") for p in parsed_data["people"] if p.get("relation")]
            ))
        
        persona.last_updated_from = "import"
        persona.maturity_score = min(persona.maturity_score + 0.1, 1.0)
        
        return persona.to_prompt_dict()
    
    def build_persona_prompt_section(self, persona_data: Dict[str, Any]) -> str:
        """构建人格相关的 Prompt 片段"""
        if not persona_data:
            return ""
        
        parts = ["【用户人格画像】"]
        
        if persona_data.get("identity_summary"):
            parts.append(f"身份概要：{persona_data['identity_summary']}")
        
        if persona_data.get("identity_traits"):
            traits = "、".join(persona_data["identity_traits"][:5])
            parts.append(f"性格特质：{traits}")
        
        # 沟通风格
        formality = persona_data.get("comm_formality", 0.5)
        expressiveness = persona_data.get("comm_expressiveness", 0.5)
        directness = persona_data.get("comm_directness", 0.5)
        
        style_desc = []
        if formality > 0.6: style_desc.append("比较正式")
        elif formality < 0.4: style_desc.append("比较随意")
        if expressiveness > 0.6: style_desc.append("表达丰富")
        elif expressiveness < 0.4: style_desc.append("简洁克制")
        if directness > 0.6: style_desc.append("直接")
        elif directness < 0.4: style_desc.append("委婉")
        
        if style_desc:
            parts.append(f"沟通风格：{'、'.join(style_desc)}")
        
        # 思维方式
        analytical = persona_data.get("thinking_analytical", 0.5)
        creative = persona_data.get("thinking_creative", 0.5)
        thinking_desc = []
        if analytical > 0.6: thinking_desc.append("偏分析型")
        if creative > 0.6: thinking_desc.append("偏创造型")
        if thinking_desc:
            parts.append(f"思维方式：{'、'.join(thinking_desc)}")
        
        # 当前目标
        goals = persona_data.get("current_goals", [])
        if goals:
            active_goals = [g for g in goals if g.get("status") == "active"]
            if active_goals:
                goal_strs = [g.get("goal", "") for g in active_goals[:3]]
                parts.append(f"当前目标：{'、'.join(goal_strs)}")
        
        return "\n".join(parts)
    
    def _clamp(self, value: float) -> float:
        """限制在 0-1 范围内"""
        return max(self.min_dimension, min(self.max_dimension, value))


# 全局实例
persona_engine = PersonaEngine()
