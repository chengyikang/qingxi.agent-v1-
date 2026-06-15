"""
信任计算引擎
分析用户消息，计算信任增长值
"""
from typing import Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.llm import llm_service


TRUST_PROMPT_TEMPLATE = """你是一个信任分析专家。请分析用户消息，判断其中包含的信任表达类型和强度。

用户消息: {message}

请从以下几个方面分析（每个方面只返回一个整数分数，如果该项不适用则返回0）:
1. 分享个人经历/故事: 0-15分
2. 分享烦恼/困扰/问题: 0-20分
3. 分享梦想/愿望/目标: 0-20分
4. 表达感谢/认可: 0-10分
5. 情绪表达（悲伤、焦虑、愤怒等）: 0-8分
6. 寻求建议/帮助: 0-15分

只回答一个JSON格式的分数列表，格式如下:
{{"experience": 数字, "troubles": 数字, "dreams": 数字, "gratitude": 数字, "emotion": 数字, "advice": 数字}}

只返回JSON，不要有其他文字。"""


class TrustEngine:
    """信任计算引擎"""
    
    def __init__(self):
        """初始化信任引擎"""
        self.max_trust_per_message = 30  # 单条消息最大信任增长
    
    async def analyze_message(self, message: str) -> Dict[str, int]:
        """
        分析用户消息，识别信任表达
        
        Args:
            message: 用户消息内容
            
        Returns:
            各类型信任表达的分数
        """
        try:
            prompt = TRUST_PROMPT_TEMPLATE.format(message=message)
            result = await llm_service.analysis(
                prompt=prompt,
                system_message="你是一个信任分析专家，只返回JSON格式的分析结果。"
            )
            
            # 解析结果
            if isinstance(result, str):
                import json
                result = json.loads(result)
            
            # 确保返回完整字段
            return {
                "experience": result.get("experience", 0),
                "troubles": result.get("troubles", 0),
                "dreams": result.get("dreams", 0),
                "gratitude": result.get("gratitude", 0),
                "emotion": result.get("emotion", 0),
                "advice": result.get("advice", 0)
            }
        except Exception:
            # 分析失败时返回默认分数
            return {
                "experience": 0,
                "troubles": 0,
                "dreams": 0,
                "gratitude": 0,
                "emotion": 0,
                "advice": 0
            }
    
    def calculate_trust_growth(self, analysis: Dict[str, int]) -> int:
        """
        根据分析结果计算信任增长值
        
        Args:
            analysis: 各类型信任表达的分数
            
        Returns:
            信任增长值
        """
        # 计算总分
        total = sum(analysis.values())
        
        # 无意义聊天奖励（避免完全无增长）
        if total == 0:
            # 简单的寒暄或问候
            return 0
        
        # 限制最大值
        return min(total, self.max_trust_per_message)
    
    def get_trust_type_description(self, analysis: Dict[str, int]) -> List[str]:
        """
        获取信任表达类型的描述
        
        Args:
            analysis: 各类型信任表达的分数
            
        Returns:
            信任表达类型的描述列表
        """
        descriptions = []
        if analysis.get("experience", 0) > 5:
            descriptions.append("分享经历")
        if analysis.get("troubles", 0) > 5:
            descriptions.append("分享烦恼")
        if analysis.get("dreams", 0) > 5:
            descriptions.append("分享梦想")
        if analysis.get("gratitude", 0) > 3:
            descriptions.append("表达感谢")
        if analysis.get("emotion", 0) > 3:
            descriptions.append("情绪表达")
        if analysis.get("advice", 0) > 5:
            descriptions.append("寻求建议")
        
        return descriptions


# 全局信任引擎实例
trust_engine = TrustEngine()
