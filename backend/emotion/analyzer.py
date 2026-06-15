"""
情绪分析器
分析用户消息中的情绪状态
"""
from typing import Dict, Tuple
from enum import Enum


EMOTION_PROMPT_TEMPLATE = """你是一个情绪分析专家。请分析用户消息中的情绪状态。

用户消息: {message}

请返回一个JSON格式的情绪分析结果:
{{"emotion": "情绪类型", "confidence": 置信度}}

情绪类型必须是以下之一:
- happy: 快乐、开心、愉悦
- sad: 悲伤、难过、沮丧
- anxious: 焦虑、担忧、不安
- angry: 愤怒、生气、恼怒
- lonely: 孤独、寂寞、空虚
- neutral: 中性、无明显情绪

置信度是一个0到1之间的小数，表示判断的确定程度。

只返回JSON，不要有其他文字。"""


class EmotionType(Enum):
    """情绪类型枚举"""
    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    ANGRY = "angry"
    LONELY = "lonely"
    NEUTRAL = "neutral"


class EmotionAnalyzer:
    """情绪分析器"""
    
    def __init__(self):
        """初始化情绪分析器"""
        self.emotion_descriptions = {
            "happy": "看起来你心情不错呢",
            "sad": "听起来你有些不开心",
            "anxious": "我能感受到你的担忧",
            "angry": "能感觉到你在生气",
            "lonely": "看起来你有些孤独",
            "neutral": ""
        }
    
    async def analyze(self, message: str) -> Tuple[str, float]:
        """
        分析消息中的情绪
        
        Args:
            message: 用户消息
            
        Returns:
            (情绪类型, 置信度)
        """
        try:
            from services.llm import llm_service
            
            prompt = EMOTION_PROMPT_TEMPLATE.format(message=message)
            result = await llm_service.analysis(
                prompt=prompt,
                system_message="你是一个情绪分析专家，只返回JSON格式的分析结果。"
            )
            
            # 解析结果
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            emotion = result.get("emotion", "neutral")
            confidence = float(result.get("confidence", 0.5))
            
            # 验证情绪类型
            valid_emotions = [e.value for e in EmotionType]
            if emotion not in valid_emotions:
                emotion = "neutral"
            
            return emotion, min(max(confidence, 0.0), 1.0)
        except Exception:
            return "neutral", 0.5
    
    def get_emotion_response_hint(self, emotion: str) -> str:
        """
        根据情绪类型获取回应提示
        
        Args:
            emotion: 情绪类型
            
        Returns:
            回应提示
        """
        return self.emotion_descriptions.get(emotion, "")
    
    def get_emotion_intensity(self, confidence: float, emotion: str) -> str:
        """
        根据置信度获取情绪强度描述
        
        Args:
            confidence: 置信度
            emotion: 情绪类型
            
        Returns:
            情绪强度描述
        """
        if confidence < 0.5:
            return "轻微"
        elif confidence < 0.7:
            return "中等"
        elif confidence < 0.85:
            return "较强"
        else:
            return "强烈"


# 全局情绪分析器实例
emotion_analyzer = EmotionAnalyzer()
