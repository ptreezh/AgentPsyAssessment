#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一AI模型API客户端
支持Ollama本地模型和OpenRouter云模型

作者: ptreezh <3061176@qq.com>
官网: https://agentpsy.com
版权: © 2025 Portable PsyAgent. All Rights Reserved.
许可: MIT License
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging
from pathlib import Path

from integrations.openrouter_client import OpenRouterClient
from utils.ollama_client import OllamaClient

class UnifiedAPIClient:
    """统一AI模型API客户端"""

    def __init__(self, config_path: str = None):
        """
        初始化统一API客户端

        Args:
            config_path: 模型配置文件路径
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config", "models_config.json")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.openrouter_client = None
        self.ollama_client = None

        # 初始化客户端
        self._init_clients()

        self.logger = logging.getLogger(__name__)

    def _init_clients(self):
        """初始化各个API客户端"""
        # 初始化OpenRouter客户端
        if os.getenv('OPENROUTER_API_KEY'):
            self.openrouter_client = OpenRouterClient()
            self.logger.info("OpenRouter客户端初始化成功")
        else:
            self.logger.warning("未找到OpenRouter API密钥")

        # 初始化Ollama客户端
        try:
            self.ollama_client = OllamaClient()
            self.logger.info("Ollama客户端初始化成功")
        except Exception as e:
            self.logger.warning(f"Ollama客户端初始化失败: {e}")

    def get_available_models(self) -> Dict[str, List[Dict]]:
        """
        获取所有可用的模型列表

        Returns:
            按提供商分组的可用模型列表
        """
        models = {
            "openrouter": [],
            "ollama": []
        }

        # 获取OpenRouter模型
        if self.openrouter_client:
            try:
                openrouter_models = asyncio.run(self.openrouter_client.get_models())
                models["openrouter"] = openrouter_models[:10]  # 只取前10个
            except Exception as e:
                self.logger.error(f"获取OpenRouter模型失败: {e}")

        # 获取Ollama模型
        if self.ollama_client:
            try:
                ollama_models = self.ollama_client.list_models()
                models["ollama"] = [{"name": model, "provider": "ollama"} for model in ollama_models]
            except Exception as e:
                self.logger.error(f"获取Ollama模型失败: {e}")

        return models

    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        provider: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一的聊天完成接口

        Args:
            model: 模型名称
            messages: 消息列表
            provider: 提供商 (openrouter, ollama, auto)
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            API响应结果
        """
        if provider == "auto":
            provider = self._detect_provider(model)

        # 使用OpenRouter
        if provider == "openrouter" or (provider is None and model.startswith("anthropic/") or
                                       model.startswith("openai/") or model.startswith("google/") or
                                       model.startswith("meta-llama/") or model.startswith("mistralai/") or
                                       model.startswith("qwen/")):
            if not self.openrouter_client:
                raise Exception("OpenRouter客户端未初始化，请检查OPENROUTER_API_KEY环境变量")

            return self.openrouter_client.sync_chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

        # 使用Ollama
        elif provider == "ollama" or provider is None:
            if not self.ollama_client:
                raise Exception("Ollama客户端未初始化，请检查Ollama服务是否运行")

            # 转换消息格式
            prompt = self._convert_messages_to_prompt(messages)

            return self.ollama_client.generate(
                model=model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )

        else:
            raise ValueError(f"不支持的提供商: {provider}")

    def _detect_provider(self, model: str) -> str:
        """
        根据模型名称自动检测提供商

        Args:
            model: 模型名称

        Returns:
            提供商名称
        """
        if "/" in model:
            return "openrouter"
        else:
            return "ollama"

    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        将消息格式转换为Ollama使用的prompt格式

        Args:
            messages: 消息列表

        Returns:
            转换后的prompt
        """
        prompt_parts = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        return "\n\n".join(prompt_parts)

    def get_model_info(self, model: str, provider: str = None) -> Dict[str, Any]:
        """
        获取模型信息

        Args:
            model: 模型名称
            provider: 提供商

        Returns:
            模型信息
        """
        if provider == "auto":
            provider = self._detect_provider(model)

        if provider == "openrouter" and self.openrouter_client:
            return self.openrouter_client.get_model_info(model)
        elif provider == "ollama":
            # Ollama模型基本信息
            return {
                "name": model,
                "provider": "ollama",
                "description": f"Ollama本地模型: {model}",
                "context_window": 4096,
                "pricing": {"input": 0, "output": 0}  # 本地模型免费
            }
        else:
            return {
                "name": model,
                "provider": "unknown",
                "description": "未知模型",
                "context_window": 4096,
                "pricing": {"input": 0, "output": 0}
            }

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int, provider: str = None) -> float:
        """
        计算API调用成本

        Args:
            model: 模型名称
            input_tokens: 输入token数量
            output_tokens: 输出token数量
            provider: 提供商

        Returns:
            成本（美元）
        """
        if provider == "auto":
            provider = self._detect_provider(model)

        if provider == "openrouter" and self.openrouter_client:
            return self.openrouter_client.calculate_cost(model, input_tokens, output_tokens)
        elif provider == "ollama":
            return 0.0  # 本地模型免费
        else:
            return 0.0

    def get_recommended_models(self, task_type: str = "evaluation") -> List[Dict[str, str]]:
        """
        根据任务类型推荐模型

        Args:
            task_type: 任务类型 (evaluation, analysis, creative, fast)

        Returns:
            推荐的模型列表
        """
        recommendations = []

        # 评估任务推荐
        if task_type == "evaluation":
            recommendations = [
                {"model": "anthropic/claude-3.5-sonnet", "provider": "openrouter", "reason": "高质量评估，精确分析"},
                {"model": "openai/gpt-4o", "provider": "openrouter", "reason": "平衡性能与速度"},
                {"model": "anthropic/claude-3-opus", "provider": "openrouter", "reason": "顶级推理能力"},
                {"model": "llama3.1", "provider": "ollama", "reason": "本地高质量模型"}
            ]

        # 分析任务推荐
        elif task_type == "analysis":
            recommendations = [
                {"model": "anthropic/claude-3.5-sonnet", "provider": "openrouter", "reason": "深度分析能力"},
                {"model": "openai/gpt-4o", "provider": "openrouter", "reason": "快速准确分析"},
                {"model": "google/gemini-pro", "provider": "openrouter", "reason": "性价比高"},
                {"model": "qwen2.5", "provider": "ollama", "reason": "本地中文优势"}
            ]

        # 创意任务推荐
        elif task_type == "creative":
            recommendations = [
                {"model": "anthropic/claude-3-opus", "provider": "openrouter", "reason": "顶级创意能力"},
                {"model": "openai/gpt-4o", "provider": "openrouter", "reason": "多模态创意"},
                {"model": "mistral-large", "provider": "openrouter", "reason": "创意表现优秀"}
            ]

        # 快速任务推荐
        elif task_type == "fast":
            recommendations = [
                {"model": "anthropic/claude-3-haiku", "provider": "openrouter", "reason": "快速响应"},
                {"model": "llama3.1", "provider": "ollama", "reason": "本地快速"},
                {"model": "mistral", "provider": "ollama", "reason": "轻量快速"}
            ]

        return recommendations

    def test_connection(self, provider: str = None) -> Dict[str, bool]:
        """
        测试到各个提供商的连接

        Args:
            provider: 要测试的提供商，如果为None则测试所有

        Returns:
            连接测试结果
        """
        results = {}

        if provider is None or provider == "openrouter":
            results["openrouter"] = self._test_openrouter_connection()

        if provider is None or provider == "ollama":
            results["ollama"] = self._test_ollama_connection()

        return results

    def _test_openrouter_connection(self) -> bool:
        """测试OpenRouter连接"""
        if not self.openrouter_client:
            return False

        try:
            models = asyncio.run(self.openrouter_client.get_models())
            return len(models) > 0
        except:
            return False

    def _test_ollama_connection(self) -> bool:
        """测试Ollama连接"""
        if not self.ollama_client:
            return False

        try:
            models = self.ollama_client.list_models()
            return len(models) >= 0
        except:
            return False


# 便捷函数
def create_unified_client(config_path: str = None) -> UnifiedAPIClient:
    """
    创建统一API客户端实例

    Args:
        config_path: 配置文件路径

    Returns:
        统一API客户端实例
    """
    return UnifiedAPIClient(config_path=config_path)


# 默认客户端实例
default_client = None

def get_default_client() -> UnifiedAPIClient:
    """
    获取默认的统一API客户端实例

    Returns:
        默认客户端实例
    """
    global default_client
    if default_client is None:
        default_client = UnifiedAPIClient()
    return default_client