#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenRouter API 客户端
支持多种AI模型的统一接口
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

class OpenRouterClient:
    """OpenRouter API客户端"""

    def __init__(self, api_key: str = None):
        """
        初始化OpenRouter客户端

        Args:
            api_key: OpenRouter API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API密钥未设置，请设置环境变量OPENROUTER_API_KEY或传入api_key参数")

        self.base_url = "https://openrouter.ai/api/v1"
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()

    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用OpenRouter聊天完成API

        Args:
            model: 模型名称，如 "anthropic/claude-3.5-sonnet"
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            **kwargs: 其他参数

        Returns:
            API响应结果
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ptreezh/AgentPsyAssessment",
            "X-Title": "Portable PsyAgent - 心理评估系统"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            **kwargs
        }

        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"OpenRouter API调用成功: {model}")
                    return result
                else:
                    error_text = await response.text()
                    self.logger.error(f"OpenRouter API调用失败: {response.status} - {error_text}")
                    raise Exception(f"OpenRouter API调用失败: {response.status}")

        except asyncio.TimeoutError:
            self.logger.error("OpenRouter API调用超时")
            raise Exception("OpenRouter API调用超时")

        except Exception as e:
            self.logger.error(f"OpenRouter API调用异常: {e}")
            raise

    async def get_models(self) -> List[Dict[str, Any]]:
        """
        获取可用的模型列表

        Returns:
            模型列表
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with self.session.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", [])
                else:
                    error_text = await response.text()
                    raise Exception(f"获取模型列表失败: {response.status} - {error_text}")

        except Exception as e:
            self.logger.error(f"获取OpenRouter模型列表异常: {e}")
            raise

    def sync_chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        同步调用聊天完成API

        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            API响应结果
        """
        async def _async_call():
            async with self:
                return await self.chat_completion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

        return asyncio.run(_async_call())

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取特定模型的信息

        Args:
            model: 模型名称

        Returns:
            模型信息
        """
        # 预定义的模型信息
        model_info = {
            "anthropic/claude-3.5-sonnet": {
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "description": "最强大的模型，适合复杂推理",
                "context_window": 200000,
                "pricing": {"input": 0.000003, "output": 0.000015}
            },
            "anthropic/claude-3-opus": {
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "description": "顶级推理模型，最适合复杂分析",
                "context_window": 200000,
                "pricing": {"input": 0.000015, "output": 0.000075}
            },
            "anthropic/claude-3-haiku": {
                "name": "Claude 3 Haiku",
                "provider": "Anthropic",
                "description": "快速响应模型，适合简单任务",
                "context_window": 200000,
                "pricing": {"input": 0.00000025, "output": 0.00000125}
            },
            "openai/gpt-4o": {
                "name": "GPT-4o",
                "provider": "OpenAI",
                "description": "高性能多模态模型",
                "context_window": 128000,
                "pricing": {"input": 0.000005, "output": 0.000015}
            },
            "openai/gpt-4-turbo": {
                "name": "GPT-4 Turbo",
                "provider": "OpenAI",
                "description": "平衡性能与速度",
                "context_window": 128000,
                "pricing": {"input": 0.00001, "output": 0.00003}
            },
            "meta-llama/llama-3.1-405b-instruct": {
                "name": "Llama 3.1 405B Instruct",
                "provider": "Meta",
                "description": "开源大模型，成本较低",
                "context_window": 131072,
                "pricing": {"input": 0.0000027, "output": 0.0000027}
            },
            "meta-llama/llama-3.1-70b-instruct": {
                "name": "Llama 3.1 70B Instruct",
                "provider": "Meta",
                "description": "开源大模型，性价比高",
                "context_window": 131072,
                "pricing": {"input": 0.00000035, "output": 0.00000035}
            },
            "mistralai/mistral-large": {
                "name": "Mistral Large",
                "provider": "Mistral AI",
                "description": "高性能开源模型",
                "context_window": 32768,
                "pricing": {"input": 0.000002, "output": 0.000006}
            }
        }

        return model_info.get(model, {
            "name": model,
            "provider": "Unknown",
            "description": "未知模型",
            "context_window": 4096,
            "pricing": {"input": 0.00001, "output": 0.00001}
        })

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        计算API调用成本

        Args:
            model: 模型名称
            input_tokens: 输入token数量
            output_tokens: 输出token数量

        Returns:
            成本（美元）
        """
        model_info = self.get_model_info(model)
        pricing = model_info.get("pricing", {"input": 0.00001, "output": 0.00001})

        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]

        return input_cost + output_cost


# 便捷函数
def create_openrouter_client(api_key: str = None) -> OpenRouterClient:
    """
    创建OpenRouter客户端实例

    Args:
        api_key: API密钥

    Returns:
        OpenRouter客户端实例
    """
    return OpenRouterClient(api_key=api_key)


# 预定义的模型配置
OPENROUTER_MODELS = {
    "claude_3_5_sonnet": "anthropic/claude-3.5-sonnet",
    "claude_3_opus": "anthropic/claude-3-opus",
    "claude_3_haiku": "anthropic/claude-3-haiku",
    "gpt_4o": "openai/gpt-4o",
    "gpt_4_turbo": "openai/gpt-4-turbo",
    "llama_3_1_405b": "meta-llama/llama-3.1-405b-instruct",
    "llama_3_1_70b": "meta-llama/llama-3.1-70b-instruct",
    "mistral_large": "mistralai/mistral-large"
}

# 评估专用的高质量模型
EVALUATION_MODELS = {
    "anthropic/claude-3.5-sonnet": {
        "quality": "excellent",
        "speed": "medium",
        "cost": "medium"
    },
    "anthropic/claude-3-opus": {
        "quality": "excellent",
        "speed": "slow",
        "cost": "high"
    },
    "openai/gpt-4o": {
        "quality": "excellent",
        "speed": "fast",
        "cost": "medium"
    }
}