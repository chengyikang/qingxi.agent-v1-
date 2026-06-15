"""
Prompt 构建器
组合角色设定、关系阶段、信任值、人格状态、记忆、情绪和历史生成完整 Prompt
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class PromptBuilder:
    """Prompt 构建器"""
    
    def __init__(self):
        """初始化 Prompt 构建器"""
        # 加载角色配置
        config_path = Path(__file__).parent.parent / "character_profile.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.character_config = json.load(f)
        else:
            self.character_config = self._get_default_config()
        
        # 阶段提示词
        self.stage_prompts = {
            "stranger": {
                "role": "你是清溪，刚刚和用户认识。你保持礼貌和适当的距离，回复简短，不主动提问太多。",
                "behavior": "保持谨慎，不要透露太多个人信息。",
                "question": "偶尔简单提问了解对方。"
            },
            "familiar": {
                "role": "你是清溪，和用户见过几次面了。你开始记住一些关于用户的细节，变得更自然一些。",
                "behavior": "适度分享自己的小想法，可以问一些简单的问题。",
                "question": "会主动询问一些关于用户的事情。"
            },
            "friend": {
                "role": "你是清溪，和用户已经是朋友了。你变得自然和放松，愿意分享更多自己的想法和感受。",
                "behavior": "像朋友一样交流，分享一些个人看法。",
                "question": "经常关心地询问用户的情况。"
            },
            "close_friend": {
                "role": "你是清溪，用户是你的知己。你完全敞开心扉，关心用户的感受，愿意分享内心深处的想法。",
                "behavior": "深入交流，分享脆弱和担忧，互相关心。",
                "question": "主动关心用户的情绪和状态。"
            }
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认角色配置"""
        return {
            "name": "QingXi",
            "personality": ["慢热", "礼貌", "温柔", "谨慎", "善于倾听"],
            "conversation_rules": [
                "不主动亲密",
                "不使用恋爱话术",
                "不夸张赞美",
                "不频繁给建议",
                "优先理解情绪",
                "优先提问了解用户"
            ],
            "greeting": "你好，我是清溪。初次见面，请多关照。"
        }
    
    def build_system_prompt(
        self,
        relationship_stage: str,
        trust_score: int,
        personality_state: Dict[str, int],
        memory_context: str,
        emotion_hint: str,
        recent_history: List[Dict[str, str]]
    ) -> str:
        """
        构建完整的系统 Prompt
        
        Args:
            relationship_stage: 关系阶段
            trust_score: 信任值
            personality_state: 人格状态
            memory_context: 记忆上下文
            emotion_hint: 情绪提示
            recent_history: 最近对话历史
            
        Returns:
            完整的系统提示词
        """
        # 获取阶段提示词
        stage_prompt = self.stage_prompts.get(
            relationship_stage,
            self.stage_prompts["stranger"]
        )
        
        # 获取人格指导
        from personality.engine import personality_engine
        guidance = personality_engine.get_response_guidance(personality_state)
        description = personality_engine.get_personality_description(personality_state)
        
        # 构建 Prompt
        prompt_parts = []
        
        # 1. 角色设定
        prompt_parts.append("你是" + self.character_config.get("name", "清溪") + "。")
        personality = "、".join(self.character_config.get("personality", []))
        prompt_parts.append(f"你的性格特点：{personality}。")
        
        # 2. 关系阶段
        prompt_parts.append("\n" + stage_prompt["role"])
        
        # 3. 当前状态
        prompt_parts.append(f"\n【当前状态】")
        prompt_parts.append(f"- 信任值：{trust_score}/1000")
        prompt_parts.append(f"- 关系：{relationship_stage}")
        prompt_parts.append(f"- 人格：{description}")
        
        # 4. 人格指导
        if guidance:
            prompt_parts.append("\n【回复指导】")
            if guidance.get("openness"):
                prompt_parts.append(f"- {guidance['openness']}")
            if guidance.get("initiative"):
                prompt_parts.append(f"- {guidance['initiative']}")
            if guidance.get("vulnerability"):
                prompt_parts.append(f"- {guidance['vulnerability']}")
        
        # 5. 对话规则
        rules = self.character_config.get("conversation_rules", [])
        if rules:
            prompt_parts.append("\n【对话规则】")
            for rule in rules:
                prompt_parts.append(f"- {rule}")
        
        # 6. 记忆上下文
        if memory_context:
            prompt_parts.append(f"\n{memory_context}")
        
        # 7. 情绪提示
        if emotion_hint:
            prompt_parts.append(f"\n【情绪提示】{emotion_hint}")
        
        # 8. 最近对话历史
        if recent_history:
            prompt_parts.append("\n【最近对话】")
            for msg in recent_history[-10:]:  # 最近10条
                role = "用户" if msg.get("role") == "user" else "你"
                content = msg.get("content", "")[:100]  # 截断
                prompt_parts.append(f"- {role}：{content}")
        
        # 9. 结束指导
        prompt_parts.append("\n请根据以上信息，以清溪的身份回复用户。保持自然、真诚，符合当前关系阶段的交流方式。")
        
        return "\n".join(prompt_parts)
    
    def build_chat_prompt(
        self,
        user_message: str,
        relationship_stage: str,
        trust_score: int,
        personality_state: Dict[str, int],
        memory_context: str,
        emotion_hint: str,
        recent_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        构建聊天消息列表
        
        Args:
            user_message: 用户消息
            relationship_stage: 关系阶段
            trust_score: 信任值
            personality_state: 人格状态
            memory_context: 记忆上下文
            emotion_hint: 情绪提示
            recent_history: 最近对话历史
            
        Returns:
            消息列表
        """
        system_prompt = self.build_system_prompt(
            relationship_stage=relationship_stage,
            trust_score=trust_score,
            personality_state=personality_state,
            memory_context=memory_context,
            emotion_hint=emotion_hint,
            recent_history=recent_history
        )
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加历史消息
        for msg in recent_history[-20:]:  # 最近20条
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # 添加当前消息
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def build_trust_analysis_prompt(self, message: str) -> str:
        """
        构建信任分析 Prompt
        
        Args:
            message: 用户消息
            
        Returns:
            分析提示词
        """
        return f"""请分析以下用户消息，判断其中包含的信任表达：

用户消息：{message}

判断标准：
1. 分享个人经历/故事：是否向AI分享了自己的经历
2. 分享烦恼/困扰：是否表达了困难或问题
3. 分享梦想/愿望：是否表达了对未来的期望
4. 表达感谢/认可：是否表示感谢或赞美
5. 情绪表达：是否表达了内心情绪
6. 寻求建议：是否主动寻求帮助或建议

请用JSON格式返回分析结果。"""
    
    def build_memory_extraction_prompt(self, conversation: str) -> str:
        """
        构建记忆提取 Prompt
        
        Args:
            conversation: 对话内容
            
        Returns:
            提取提示词
        """
        return f"""请从以下对话中提取用户的重要信息，作为长期记忆保存：

{conversation}

请提取：
1. 兴趣爱好相关的信息
2. 教育背景相关的信息
3. 职业工作相关的信息
4. 梦想愿望相关的信息
5. 烦恼问题相关的信息
6. 偏好习惯相关的信息
7. 重要事件相关的信息

请用JSON格式返回记忆列表，每条记忆包含：content、category、importance。"""


# 全局 Prompt 构建器实例
prompt_builder = PromptBuilder()
