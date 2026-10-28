"""LLM 服务 - 多提供商"""
import json
import logging
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI, OpenAIError
from config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self._model: str = ""
        self._provider: str = ""
        self._initialized: bool = False
    
    def _ensure_init(self):
        if self._initialized: return
        config = settings.get_llm_config()
        api_key = config["api_key"]
        base_url = config["base_url"]
        self._model = config["model"]
        self._provider = config["provider"]
        if not api_key:
            logger.warning(f"LLM API Key 未配置！提供商: {self._provider}")
            self._initialized = True
            return
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url if base_url else None)
        self._initialized = True
        logger.info(f"LLM 已初始化 - 提供商: {self._provider}, 模型: {self._model}")
    
    @property
    def is_ready(self) -> bool:
        self._ensure_init()
        return self._client is not None
    
    async def chat_completion(self, messages, temperature=0.8, max_tokens=None) -> str:
        self._ensure_init()
        if not self._client:
            raise Exception(f"LLM 服务未就绪，请配置 LLM_API_KEY。提供商: {self._provider}")
        try:
            kwargs = {"model": self._model, "messages": messages, "temperature": temperature}
            if max_tokens: kwargs["max_tokens"] = max_tokens
            response = await self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except OpenAIError as e:
            raise Exception(f"LLM API 调用失败 ({self._provider}): {str(e)}")
    
    async def structured_completion(self, messages, response_format=None) -> Dict[str, Any]:
        self._ensure_init()
        if not self._client:
            raise Exception(f"LLM 服务未就绪，提供商: {self._provider}")
        try:
            kwargs = {"model": self._model, "messages": messages, "temperature": 0.3}
            if response_format: kwargs["response_format"] = response_format
            response = await self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or "{}"
            if content.startswith("```json"): content = content[7:]
            if content.startswith("```"): content = content[3:]
            if content.endswith("```"): content = content[:-3]
            return json.loads(content.strip())
        except (OpenAIError, json.JSONDecodeError) as e:
            raise Exception(f"结构化输出解析失败 ({self._provider}): {str(e)}")
    
    async def analysis(self, prompt, system_message=None, temperature=0.3) -> str:
        messages = []
        if system_message: messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        return await self.chat_completion(messages, temperature=temperature)


llm_service = LLMService()
