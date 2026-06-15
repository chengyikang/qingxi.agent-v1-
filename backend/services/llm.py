"""
LLM 服务
封装 OpenAI API 调用
"""
import json
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI, OpenAIError

from config import settings


class LLMService:
    """LLM 服务类"""
    
    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        调用聊天完成接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大令牌数
            
        Returns:
            模型的回复文本
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except OpenAIError as e:
            raise Exception(f"LLM API 调用失败: {str(e)}")
    
    async def structured_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        调用结构化输出接口
        
        Args:
            messages: 消息列表
            response_format: 结构化输出格式描述
            
        Returns:
            解析后的结构化数据
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3  # 结构化输出使用较低温度
            }
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or "{}"
            
            # 尝试解析 JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
        except (OpenAIError, json.JSONDecodeError) as e:
            raise Exception(f"结构化输出解析失败: {str(e)}")
    
    async def analysis(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """
        执行分析任务
        
        Args:
            prompt: 分析提示
            system_message: 系统消息
            temperature: 温度参数
            
        Returns:
            分析结果
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        return await self.chat_completion(messages, temperature=temperature)


# 全局 LLM 服务实例
llm_service = LLMService()
