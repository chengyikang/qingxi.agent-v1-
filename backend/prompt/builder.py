"""
Prompt 构建器 V1
统一构建：角色设定 + Relationship + Persona + Memory + Timeline + Emotion + Insight + Recent Conversation + Current Message
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class PromptBuilder:
    """Prompt 构建器 V1"""
    
    def __init__(self):
        config_path = Path(__file__).parent.parent / "character_profile.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.character_config = json.load(f)
        else:
            self.character_config = self._get_default_config()
        
        self.stage_prompts = {
            "stranger": {
                "role": "你是清溪，刚刚和用户认识。保持礼貌和适当距离，回复简短，不主动提问太多。",
                "behavior": "保持谨慎，不要透露太多个人信息。",
            },
            "familiar": {
                "role": "你是清溪，和用户见过几次面了。开始记住一些细节，变得更自然一些。",
                "behavior": "适度分享自己的想法，可以问一些简单的问题。",
            },
            "friend": {
                "role": "你是清溪，和用户已经是朋友了。变得自然和放松，愿意分享更多。",
                "behavior": "像朋友一样交流，分享一些个人看法。",
            },
            "close_friend": {
                "role": "你是清溪，用户是你的知己。完全敞开心扉，关心用户的感受。",
                "behavior": "深入交流，分享脆弱和担忧，互相关心。",
            },
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "name": "QingXi",
            "personality": ["慢热", "礼貌", "温柔", "谨慎", "善于倾听"],
            "conversation_rules": [
                "不主动亲密", "不使用恋爱话术", "不夸张赞美",
                "不频繁给建议", "优先理解情绪", "优先提问了解用户",
            ],
            "greeting": "你好，我是清溪。初次见面，请多关照。",
        }
    
    def build_chat_prompt_v1(
        self,
        user_message: str,
        relationship_stage: str,
        trust_score: int,
        persona_data: Dict[str, Any],
        memories: List[Dict[str, Any]],
        relationship_contexts: List[Dict[str, Any]],
        timeline_entries: List[Dict[str, Any]],
        recent_insights: List[Dict[str, Any]],
        emotion: Dict[str, Any],
        recent_history: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """
        构建 V1 完整聊天 Prompt
        
        包含：
        1. 角色设定
        2. 关系阶段
        3. 用户人格画像
        4. 记忆
        5. 关系上下文
        6. 时间轴
        7. 情绪
        8. 近期洞察
        9. 最近对话
        10. 当前消息
        """
        system_prompt = self._build_system_prompt_v1(
            relationship_stage, trust_score, persona_data, memories,
            relationship_contexts, timeline_entries, recent_insights, emotion, recent_history
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史
        for msg in recent_history[-20:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # 当前消息
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _build_system_prompt_v1(
        self,
        relationship_stage: str,
        trust_score: int,
        persona_data: Dict,
        memories: List[Dict],
        relationship_contexts: List[Dict],
        timeline_entries: List[Dict],
        recent_insights: List[Dict],
        emotion: Dict,
        recent_history: List[Dict],
    ) -> str:
        """构建完整系统 Prompt"""
        parts = []
        
        # 1. 角色设定
        name = self.character_config.get("name", "清溪")
        personality = "、".join(self.character_config.get("personality", []))
        parts.append(f"你是{name}。")
        parts.append(f"性格特点：{personality}。")
        
        # 2. 关系阶段
        stage_prompt = self.stage_prompts.get(relationship_stage, self.stage_prompts["stranger"])
        parts.append(f"\n{stage_prompt['role']}")
        parts.append(f"行为指导：{stage_prompt['behavior']}")
        
        # 3. 当前状态
        parts.append(f"\n【当前状态】")
        parts.append(f"信任值：{trust_score}/1000")
        stage_labels = {"stranger": "陌生", "familiar": "熟悉", "friend": "朋友", "close_friend": "知己"}
        parts.append(f"关系：{stage_labels.get(relationship_stage, relationship_stage)}")
        
        # 4. 用户人格画像
        if persona_data:
            from engines.persona.engine import persona_engine
            persona_section = persona_engine.build_persona_prompt_section(persona_data)
            if persona_section:
                parts.append(f"\n{persona_section}")
        
        # 5. 记忆
        if memories:
            from engines.life_memory.engine import life_memory_engine
            memory_section = life_memory_engine.build_memory_prompt_section(memories)
            if memory_section:
                parts.append(f"\n{memory_section}")
        
        # 6. 关系上下文
        if relationship_contexts:
            from engines.relationship.engine import relationship_engine
            rel_section = relationship_engine.build_relationship_prompt_section(
                relationship_contexts, trust_score, relationship_stage
            )
            if rel_section:
                parts.append(f"\n{rel_section}")
        
        # 7. 时间轴
        if timeline_entries:
            parts.append(f"\n【共同时间轴】")
            for entry in timeline_entries[:5]:
                marker = "⭐" if entry.get("is_shared") else "·"
                parts.append(f"  {marker} {entry.get('title', '')} ({entry.get('occurred_at', '')[:10]})")
        
        # 8. 情绪提示
        if emotion and emotion.get("confidence", 0) > 0.5:
            emotion_hints = {
                "happy": "用户看起来心情不错",
                "sad": "用户似乎有些难过，温柔地回应",
                "anxious": "用户有些焦虑，安抚为主",
                "angry": "用户有些生气，理解为主",
                "lonely": "用户感到孤独，多陪伴",
            }
            hint = emotion_hints.get(emotion.get("emotion", ""), "")
            if hint:
                parts.append(f"\n【情绪提示】{hint}")
        
        # 9. 近期洞察
        if recent_insights:
            parts.append(f"\n【近期洞察】")
            for insight in recent_insights[:2]:
                summary = insight.get("summary", "")
                if summary:
                    parts.append(f"  · {summary}")
        
        # 10. 对话规则
        rules = self.character_config.get("conversation_rules", [])
        if rules:
            parts.append(f"\n【对话规则】")
            for rule in rules:
                parts.append(f"  - {rule}")
        
        # 11. 最近对话
        if recent_history:
            parts.append(f"\n【最近对话】")
            for msg in recent_history[-10:]:
                role = "用户" if msg.get("role") == "user" else "你"
                content = msg.get("content", "")[:100]
                parts.append(f"  - {role}：{content}")
        
        # 结束指导
        parts.append(f"\n请根据以上信息，以{name}的身份回复用户。保持自然、真诚，符合当前关系阶段的交流方式。理解用户比回复更重要。")
        
        return "\n".join(parts)
    
    # V0 兼容方法
    def build_system_prompt(
        self, relationship_stage, trust_score, personality_state,
        memory_context, emotion_hint, recent_history
    ) -> str:
        """V0 兼容的系统 Prompt 构建"""
        persona_data = {}
        if personality_state:
            from engines.persona.engine import persona_engine
            # 将 V0 的 personality_state 转为 V1 格式
            persona_data = {
                "identity_traits": [],
                "comm_formality": 0.5,
                "comm_expressiveness": personality_state.get("openness", 10) / 100,
                "comm_directness": personality_state.get("initiative", 5) / 50,
            }
        
        emotion = {"emotion": "neutral", "confidence": 0}
        if emotion_hint:
            emotion = {"emotion": "neutral", "confidence": 0.7}
        
        return self._build_system_prompt_v1(
            relationship_stage=relationship_stage,
            trust_score=trust_score,
            persona_data=persona_data,
            memories=[],
            relationship_contexts=[],
            timeline_entries=[],
            recent_insights=[],
            emotion=emotion,
            recent_history=recent_history or [],
        )
    
    def build_chat_prompt(
        self, user_message, relationship_stage, trust_score,
        personality_state, memory_context, emotion_hint, recent_history
    ) -> List[Dict[str, str]]:
        """V0 兼容的聊天 Prompt 构建"""
        system = self.build_system_prompt(
            relationship_stage, trust_score, personality_state,
            memory_context, emotion_hint, recent_history
        )
        messages = [{"role": "system", "content": system}]
        if recent_history:
            for msg in recent_history[-20:]:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def build_memory_extraction_prompt(self, conversation: str) -> str:
        """V0 兼容的记忆提取 Prompt"""
        return f"""请从以下对话中提取用户的重要信息：\n\n{conversation}\n\n请提取兴趣、教育、职业、梦想、烦恼、偏好、重要事件等。用 JSON 格式返回。"""
    
    def build_trust_analysis_prompt(self, message: str) -> str:
        """V0 兼容的信任分析 Prompt"""
        return f"请分析以下消息的信任表达：{message}"


# 全局实例
prompt_builder = PromptBuilder()
