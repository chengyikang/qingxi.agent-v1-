"""
Module 02: Life Parser
理解导入内容，自动提取人物、时间、地点、兴趣、目标、梦想、情绪、人生事件、成长经历
输出结构化人生数据
"""
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class LifeParserEngine:
    """人生解析引擎"""
    
    def __init__(self):
        self.max_content_length = 50000  # 最大处理内容长度
        self.chunk_size = 3000  # 分块大小
    
    async def parse(
        self,
        content: str,
        source_type: str = "txt",
        parsed_messages: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        解析内容，提取结构化人生数据
        
        Returns:
            {
                "people": [...],       # 提取的人物
                "interests": [...],    # 兴趣
                "goals": [...],        # 目标
                "dreams": [...],       # 梦想
                "emotions": [...],     # 情绪特点
                "life_events": [...],  # 人生事件
                "growth": [...],       # 成长经历
                "relationships": [...],# 关系
                "preferences": [...],  # 偏好
                "values": [...],       # 价值观
            }
        """
        # 截断过长内容
        content = content[:self.max_content_length]
        
        # 尝试 LLM 解析
        try:
            result = await self._parse_with_llm(content, source_type, parsed_messages)
        except Exception as e:
            logger.warning(f"LLM 解析失败，使用规则解析: {e}")
            result = self._parse_with_rules(content, source_type, parsed_messages)
        
        return result
    
    async def _parse_with_llm(
        self,
        content: str,
        source_type: str,
        parsed_messages: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """使用 LLM 解析"""
        from services.llm import llm_service
        
        # 构建内容摘要（如果太长就分块）
        if len(content) > self.chunk_size:
            chunks = self._split_content(content)
            # 取首尾块和中间关键块
            if len(chunks) > 3:
                working_content = chunks[0] + "\n...\n" + chunks[-1]
            else:
                working_content = content[:self.chunk_size]
        else:
            working_content = content
        
        prompt = f"""请分析以下用户人生资料，提取结构化信息。

资料类型：{source_type}
资料内容：
{working_content}

请提取以下信息，以 JSON 格式返回：

{{
  "people": [{{"name": "人物名", "relation": "关系", "mentions": 提及次数}}],
  "interests": [{{"name": "兴趣", "level": "high/medium/low", "evidence": "依据"}}],
  "goals": [{{"goal": "目标", "status": "active/achieved/abandoned", "timeframe": "时间"}}],
  "dreams": [{{"dream": "梦想", "importance": "high/medium/low"}}],
  "emotions": [{{"pattern": "情绪模式", "frequency": "frequent/occasional/rare", "context": "场景"}}],
  "life_events": [{{"title": "事件", "time": "时间", "type": "milestone/challenge/achievement", "impact": "high/medium/low"}}],
  "growth": [{{"area": "成长领域", "description": "描述", "evidence": "依据"}}],
  "relationships": [{{"with": "对象", "type": "类型", "quality": "good/neutral/strained"}}],
  "preferences": [{{"category": "类别", "preference": "偏好", "strength": "strong/moderate/weak"}}],
  "values": [{{"value": "价值观", "importance": "high/medium/low", "evidence": "依据"}}]
}}

只返回 JSON，不要其他文字。如果某些字段没有提取到，返回空数组。"""
        
        result = await llm_service.analysis(
            prompt=prompt,
            system_message="你是一个人生数据解析专家，擅长从文本中提取人物、事件、情感、成长等结构化信息。只返回 JSON。"
        )
        
        # 解析结果
        if isinstance(result, str):
            # 清理 markdown 代码块
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = json.loads(result.strip())
        
        # 确保所有字段都存在
        default_fields = {
            "people": [], "interests": [], "goals": [], "dreams": [],
            "emotions": [], "life_events": [], "growth": [],
            "relationships": [], "preferences": [], "values": [],
        }
        for key, default in default_fields.items():
            if key not in result or not isinstance(result[key], list):
                result[key] = default
        
        return result
    
    def _parse_with_rules(
        self,
        content: str,
        source_type: str,
        parsed_messages: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """基于规则的解析（LLM 不可用时的后备方案）"""
        result = {
            "people": [],
            "interests": [],
            "goals": [],
            "dreams": [],
            "emotions": [],
            "life_events": [],
            "growth": [],
            "relationships": [],
            "preferences": [],
            "values": [],
        }
        
        # 兴趣关键词
        interest_keywords = {
            "编程": "tech", "音乐": "art", "运动": "sport", "阅读": "reading",
            "旅行": "travel", "美食": "food", "摄影": "art", "游戏": "entertainment",
            "画画": "art", "写作": "writing", "跑步": "sport", "健身": "sport",
        }
        
        for kw, cat in interest_keywords.items():
            if kw in content:
                result["interests"].append({
                    "name": kw, "level": "medium", "evidence": f"文本中提到{kw}"
                })
        
        # 梦想关键词
        dream_keywords = ["梦想", "希望", "愿望", "想成为", "目标是", "理想", "未来想"]
        for kw in dream_keywords:
            idx = content.find(kw)
            if idx >= 0:
                snippet = content[max(0, idx-10):idx+50]
                result["dreams"].append({
                    "dream": snippet, "importance": "medium"
                })
        
        # 情绪关键词
        emotion_patterns = {
            "焦虑": "焦虑倾向", "压力": "压力模式", "孤独": "孤独感",
            "开心": "积极情绪", "难过": "消极情绪", "迷茫": "迷茫感",
        }
        for kw, pattern in emotion_patterns.items():
            count = content.count(kw)
            if count > 0:
                result["emotions"].append({
                    "pattern": pattern, "frequency": "frequent" if count > 3 else "occasional",
                    "context": f"出现{count}次"
                })
        
        # 如果有聊天记录，提取人物
        if parsed_messages:
            senders = {}
            for msg in parsed_messages:
                sender = msg.get("sender", "unknown")
                if sender and sender != "unknown":
                    senders[sender] = senders.get(sender, 0) + 1
            for name, count in sorted(senders.items(), key=lambda x: -x[1])[:10]:
                result["people"].append({
                    "name": name, "relation": "聊天对象", "mentions": count
                })
        
        return result
    
    def _split_content(self, content: str) -> List[str]:
        """分块内容"""
        chunks = []
        for i in range(0, len(content), self.chunk_size):
            chunks.append(content[i:i + self.chunk_size])
        return chunks


# 全局实例
life_parser_engine = LifeParserEngine()
