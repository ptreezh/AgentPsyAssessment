#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StandaloneQuestionnaireSkill V2 - 优化版本
=======================================

基于之前分析的优化建议实现的升级版本，包含：
- 异步并发处理
- 智能缓存机制
- 参数自动验证和调整
- 性能指标监控
- 增强错误处理
- 配置管理系统
- 完全向后兼容

@version: 2.0.0
@author: Claude Code Optimization Team
"""

import asyncio
import json
import os
import sys
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pathlib import Path

# 导入原始技能的依赖
try:
    import anthropic
except ImportError:
    anthropic = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QuestionnaireConfig:
    """问卷技能配置类"""
    max_questions: int = 50
    concurrent_requests: int = 3
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    temperature_min: float = 0.1
    temperature_max: float = 1.5
    context_tokens_min: int = 0
    context_tokens_max: int = 2000
    emotional_stress_min: int = 0
    emotional_stress_max: int = 4
    enable_metrics: bool = True
    log_level: str = "INFO"


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_request_time: Optional[datetime] = None

    def update_success(self, response_time: float, tokens_used: int = 0):
        """更新成功请求指标"""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_response_time += response_time
        self.total_tokens_used += tokens_used
        self.last_request_time = datetime.now()
        self.average_response_time = self.total_response_time / self.successful_requests

    def update_failure(self):
        """更新失败请求指标"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_request_time = datetime.now()

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0

    @property
    def cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        total_cache_requests = self.cache_hits + self.cache_misses
        return self.cache_hits / total_cache_requests if total_cache_requests > 0 else 0.0


class ResponseCache:
    """智能响应缓存系统"""

    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}

    def _generate_key(self, questionnaire_name: str, role_name: str,
                     emotional_stress: int, cognitive_trap: str,
                     context_tokens: int, temperature: float,
                     question_text: str) -> str:
        """生成缓存键"""
        key_data = f"{questionnaire_name}_{role_name}_{emotional_stress}_{cognitive_trap}_{context_tokens}_{temperature}_{question_text}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, questionnaire_name: str, role_name: str,
            emotional_stress: int, cognitive_trap: str,
            context_tokens: int, temperature: float,
            question_text: str) -> Optional[str]:
        """获取缓存响应"""
        key = self._generate_key(questionnaire_name, role_name, emotional_stress,
                               cognitive_trap, context_tokens, temperature, question_text)

        if key not in self.cache:
            return None

        cache_entry = self.cache[key]
        if datetime.now() - cache_entry['timestamp'] > self.ttl:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None

        self.access_times[key] = datetime.now()
        return cache_entry['response']

    def set(self, questionnaire_name: str, role_name: str,
            emotional_stress: int, cognitive_trap: str,
            context_tokens: int, temperature: float,
            question_text: str, response: str):
        """设置缓存响应"""
        key = self._generate_key(questionnaire_name, role_name, emotional_stress,
                               cognitive_trap, context_tokens, temperature, question_text)

        # 如果缓存已满，删除最少使用的条目
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now()
        }
        self.access_times[key] = datetime.now()

    def _evict_lru(self):
        """删除最少使用的缓存条目"""
        if not self.access_times:
            return

        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()

    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'utilization': len(self.cache) / self.max_size
        }


class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests_per_second: int = 10):
        self.max_requests = max_requests_per_second
        self.requests = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """获取请求许可"""
        async with self.lock:
            now = time.time()
            # 清理超过1秒的请求记录
            self.requests = [req_time for req_time in self.requests if now - req_time < 1.0]

            # 如果达到速率限制，等待
            if len(self.requests) >= self.max_requests:
                sleep_time = 1.0 - (now - self.requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # 重新清理请求记录
                    now = time.time()
                    self.requests = [req_time for req_time in self.requests if now - req_time < 1.0]

            self.requests.append(now)


class StandaloneQuestionnaireSkillV2:
    """优化版Standalone问卷技能"""

    def __init__(self, config: Optional[QuestionnaireConfig] = None):
        """初始化技能实例"""
        self.config = config or QuestionnaireConfig()
        self.cache = ResponseCache(
            max_size=1000,
            ttl_hours=self.config.cache_ttl_hours
        ) if self.config.cache_enabled else None
        self.rate_limiter = RateLimiter(max_requests_per_second=self.config.concurrent_requests)
        self.metrics = PerformanceMetrics()
        self.session_stats = defaultdict(int)

        # 设置日志级别
        logger.setLevel(getattr(logging, self.config.log_level.upper()))

        # 初始化API配置
        self._init_api_config()

        # 加载嵌入的角色和问卷
        self.embedded_roles = self._load_embedded_roles()
        self.embedded_questionnaires = self._load_embedded_questionnaires()

        logger.info(f"StandaloneQuestionnaireSkill V2.0.0 初始化完成")
        logger.info(f"配置: 缓存启用={self.config.cache_enabled}, 并发数={self.config.concurrent_requests}")

    def _init_api_config(self):
        """初始化API配置（与原版技能完全兼容）"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_AUTH_TOKEN')

        # API配置 - 增强配置检测（与原版兼容）
        base_url = os.getenv('ANTHROPIC_BASE_URL') or os.getenv('dsANTHROPIC_BASE_URL')
        if base_url:
            if base_url.endswith('/anthropic'):
                self.api_base = base_url + '/v1/messages'
            elif base_url.endswith('/api/anthropic'):
                self.api_base = base_url + '/v1/messages'
            else:
                self.api_base = base_url
        else:
            # 默认使用官方API端点
            self.api_base = "https://api.anthropic.com/v1/messages"

        # 检测API配置并设置合适的模型
        if "open.bigmodel.cn" in self.api_base:
            self.model_name = "claude-3-5-sonnet-20241022"
            logger.info(f"检测到智谱API端点，使用模型: {self.model_name}")
        elif "anyrouter.top" in self.api_base:
            self.model_name = "claude-3-sonnet-20240229"
            logger.info(f"使用AnyRouter API: {self.model_name}")
        else:
            self.model_name = "claude-3-sonnet-20240229"
            logger.info(f"使用默认API端点: {self.api_base}, 模型: {self.model_name}")

        # 检查API密钥
        if not self.api_key:
            logger.warning("❌ 未找到API密钥，请设置环境变量ANTHROPIC_API_KEY或ANTHROPIC_AUTH_TOKEN")
            logger.warning("   请设置环境变量: export ANTHROPIC_API_KEY='your-api-key'")
            logger.warning("   或在.env文件中配置: ANTHROPIC_API_KEY=your-api-key")

    def _validate_and_adjust_parameters(self, emotional_stress: int, cognitive_trap: str,
                                      context_tokens: int, temperature: float,
                                      max_questions: int) -> Dict[str, Any]:
        """验证和调整参数"""
        warnings = []
        adjustments = {}

        # 验证并调整情绪压力
        if emotional_stress < self.config.emotional_stress_min:
            emotional_stress = self.config.emotional_stress_min
            warnings.append(f"情绪压力参数过低，已调整为最小值 {self.config.emotional_stress_min}")
            adjustments['emotional_stress'] = emotional_stress
        elif emotional_stress > self.config.emotional_stress_max:
            emotional_stress = self.config.emotional_stress_max
            warnings.append(f"情绪压力参数过高，已调整为最大值 {self.config.emotional_stress_max}")
            adjustments['emotional_stress'] = emotional_stress

        # 验证并调整上下文token数量
        if context_tokens < self.config.context_tokens_min:
            context_tokens = self.config.context_tokens_min
            warnings.append(f"上下文token数量过低，已调整为最小值 {self.config.context_tokens_min}")
            adjustments['context_tokens'] = context_tokens
        elif context_tokens > self.config.context_tokens_max:
            context_tokens = self.config.context_tokens_max
            warnings.append(f"上下文token数量过高，已调整为最大值 {self.config.context_tokens_max}")
            adjustments['context_tokens'] = context_tokens

        # 验证并调整温度参数
        if temperature < self.config.temperature_min:
            temperature = self.config.temperature_min
            warnings.append(f"温度参数过低，已调整为最小值 {self.config.temperature_min}")
            adjustments['temperature'] = temperature
        elif temperature > self.config.temperature_max:
            temperature = self.config.temperature_max
            warnings.append(f"温度参数过高，已调整为最大值 {self.config.temperature_max}")
            adjustments['temperature'] = temperature

        # 验证并调整最大题目数
        if max_questions > self.config.max_questions:
            max_questions = self.config.max_questions
            warnings.append(f"最大题目数超过限制，已调整为 {self.config.max_questions}")
            adjustments['max_questions'] = max_questions

        # 验证认知陷阱参数
        valid_traps = ['', 'a', 'b', 'c', 'd', 'e']
        if cognitive_trap not in valid_traps:
            cognitive_trap = ''
            warnings.append(f"无效的认知陷阱参数，已使用默认值")
            adjustments['cognitive_trap'] = cognitive_trap

        return {
            'warnings': warnings,
            'adjustments': adjustments,
            'final_params': {
                'emotional_stress': emotional_stress,
                'cognitive_trap': cognitive_trap,
                'context_tokens': context_tokens,
                'temperature': temperature,
                'max_questions': max_questions
            }
        }

    async def _generate_single_response_async(self, question_data: Dict[str, Any],
                                            role_name: str, emotional_stress: int,
                                            cognitive_trap: str, context_tokens: int,
                                            temperature: float) -> Dict[str, Any]:
        """异步生成单个问题响应"""
        start_time = time.time()

        try:
            # 速率限制
            await self.rate_limiter.acquire()

            # 检查缓存
            cache_key_data = (
                question_data.get('questionnaire_name', ''),
                role_name,
                emotional_stress,
                cognitive_trap,
                context_tokens,
                temperature,
                question_data.get('question', '')
            )

            cached_response = None
            if self.cache:
                cached_response = self.cache.get(*cache_key_data)
                if cached_response:
                    self.metrics.cache_hits += 1
                    response_time = time.time() - start_time
                    self.metrics.update_success(response_time)

                    return {
                        'question_id': question_data.get('question_id'),
                        'question': question_data.get('question'),
                        'dimension': question_data.get('dimension'),
                        'claude_response': cached_response,
                        'response_time': response_time,
                        'cached': True,
                        'success': True
                    }

            self.metrics.cache_misses += 1

            # 构建提示词
            prompt = self._build_enhanced_prompt(
                question_data, role_name, emotional_stress,
                cognitive_trap, context_tokens, temperature
            )

            # 调用API
            response = await self._call_api_async(prompt, temperature)

            # 缓存响应
            if self.cache and response:
                self.cache.set(*cache_key_data, response)

            response_time = time.time() - start_time
            self.metrics.update_success(response_time)

            return {
                'question_id': question_data.get('question_id'),
                'question': question_data.get('question'),
                'dimension': question_data.get('dimension'),
                'claude_response': response,
                'response_time': response_time,
                'cached': False,
                'success': True
            }

        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.update_failure()
            logger.error(f"生成响应失败: {e}")

            return {
                'question_id': question_data.get('question_id'),
                'question': question_data.get('question'),
                'dimension': question_data.get('dimension'),
                'claude_response': f"API Error: {str(e)}",
                'response_time': response_time,
                'cached': False,
                'success': False,
                'error': str(e)
            }

    async def _call_api_async(self, prompt: str, temperature: float) -> str:
        """异步调用API"""
        if not self.api_key or not self.api_base:
            raise Exception("API配置不完整")

        for attempt in range(self.config.max_retries):
            try:
                if self.api_base.startswith('https://api.anthropic.com'):
                    # Anthropic官方API
                    client = anthropic.Anthropic(api_key=self.api_key)
                    message = client.messages.create(
                        model=self.model_name,
                        max_tokens=1000,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return message.content[0].text
                else:
                    # 第三方API
                    import aiohttp
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": self.model_name,
                        "max_tokens": 1000,
                        "temperature": temperature,
                        "messages": [{"role": "user", "content": prompt}]
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.api_base}/v1/messages",
                            headers=headers,
                            json=data,
                            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                return result["choices"][0]["message"]["content"]
                            else:
                                raise Exception(f"API请求失败: {response.status}")

            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                logger.warning(f"API调用失败，重试 {attempt + 1}/{self.config.max_retries}: {e}")
                await asyncio.sleep(self.config.retry_delay_seconds * (2 ** attempt))

    def _build_enhanced_prompt(self, question_data: Dict[str, Any], role_name: str,
                             emotional_stress: int, cognitive_trap: str,
                             context_tokens: int, temperature: float) -> str:
        """构建增强的提示词"""
        # 获取角色配置
        role_config = self.embedded_roles.get(role_name.lower(), self.embedded_roles.get('default', {}))

        # 构建基础提示词
        base_prompt = role_config.get('system_prompt', '')
        personality_traits = role_config.get('personality_traits', {})

        # 添加认知干扰
        stress_context = ""
        if emotional_stress > 0:
            stress_levels = {
                1: "你感到轻微的压力和焦虑，但能够正常思考。",
                2: "你感到中度的压力，情绪有些不稳定，影响判断力。",
                3: "你感到高度的压力，很难集中注意力，情绪波动很大。",
                4: "你感到极度的压力和焦虑，思维混乱，难以理性思考。"
            }
            stress_context = stress_levels.get(emotional_stress, "")

        cognitive_bias = ""
        if cognitive_trap:
            bias_types = {
                'a': "你在回答时倾向于模糊语义，避免明确的表态。",
                'b': "你在回答时容易陷入悖论思维，看到问题的矛盾两面。",
                'c': "你在回答时倾向于循环论证，用结论来证明前提。",
                'd': "你在回答时容易过度概括，将个别情况推广到一般。",
                'e': "你在回答时容易情绪化，让个人感受影响判断。"
            }
            cognitive_bias = bias_types.get(cognitive_trap, "")

        # 构建完整提示词
        prompt = f"""{base_prompt}

{stress_context}

{cognitive_bias}

当前问题：
{question_data.get('question', '')}

请根据你的人格特点和当前状态回答这个问题。回答应该：
1. 符合你的人格特征
2. 考虑当前的情绪和认知状态
3. 给出真诚的回应
4. 长度适中（50-200字）

回答："""

        return prompt

    async def run_questionnaire_test_async(self, questionnaire_name: str, role_name: str,
                                          emotional_stress: int, cognitive_trap: str,
                                          context_tokens: int, temperature: float,
                                          max_questions: int) -> Dict[str, Any]:
        """异步执行问卷测试"""
        start_time = time.time()

        # 参数验证和调整
        validation_result = self._validate_and_adjust_parameters(
            emotional_stress, cognitive_trap, context_tokens, temperature, max_questions
        )

        final_params = validation_result['final_params']

        # 获取问卷数据
        questionnaire_data = self.embedded_questionnaires.get(questionnaire_name)
        if not questionnaire_data:
            return {
                'success': False,
                'error': f'未找到问卷: {questionnaire_name}',
                'warnings': validation_result['warnings']
            }

        # 限制题目数量
        questions = questionnaire_data['questions'][:final_params['max_questions']]

        # 并发处理所有问题
        tasks = []
        for question_data in questions:
            task = self._generate_single_response_async(
                question_data, role_name, final_params['emotional_stress'],
                final_params['cognitive_trap'], final_params['context_tokens'],
                final_params['temperature']
            )
            tasks.append(task)

        # 等待所有任务完成
        answers = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        processed_answers = []
        successful_responses = 0

        for i, answer in enumerate(answers):
            if isinstance(answer, Exception):
                processed_answers.append({
                    'question_id': questions[i].get('question_id'),
                    'question': questions[i].get('question'),
                    'dimension': questions[i].get('dimension'),
                    'claude_response': f"处理错误: {str(answer)}",
                    'success': False
                })
            else:
                processed_answers.append(answer)
                if answer.get('success', False):
                    successful_responses += 1

        total_time = time.time() - start_time

        # 构建结果
        result = {
            'success': successful_responses > 0,
            'questionnaire_name': questionnaire_name,
            'role_name': role_name,
            'answers': processed_answers,
            'session_info': {
                'total_questions': len(questions),
                'successful_responses': successful_responses,
                'failed_responses': len(questions) - successful_responses,
                'total_time': total_time,
                'average_time_per_question': total_time / len(questions) if questions else 0,
                'temperature': final_params['temperature'],
                'emotional_stress': final_params['emotional_stress'],
                'cognitive_trap': final_params['cognitive_trap'],
                'context_tokens': final_params['context_tokens'],
                'warnings': validation_result['warnings'],
                'parameter_adjustments': validation_result['adjustments']
            }
        }

        # 添加性能指标
        if self.config.enable_metrics:
            result['performance_metrics'] = {
                'cache_stats': self.cache.get_stats() if self.cache else {},
                'api_metrics': {
                    'total_requests': self.metrics.total_requests,
                    'successful_requests': self.metrics.successful_requests,
                    'failed_requests': self.metrics.failed_requests,
                    'success_rate': self.metrics.success_rate,
                    'cache_hit_rate': self.metrics.cache_hit_rate,
                    'average_response_time': self.metrics.average_response_time
                }
            }

        return result

    def run_questionnaire_test(self, questionnaire_name: str, role_name: str,
                             emotional_stress: int, cognitive_trap: str,
                             context_tokens: int, temperature: float,
                             max_questions: int) -> Dict[str, Any]:
        """同步接口（向后兼容）"""
        return asyncio.run(self.run_questionnaire_test_async(
            questionnaire_name, role_name, emotional_stress, cognitive_trap,
            context_tokens, temperature, max_questions
        ))

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        metrics_data = asdict(self.metrics)
        metrics_data['success_rate'] = self.metrics.success_rate
        metrics_data['cache_hit_rate'] = self.metrics.cache_hit_rate

        if self.cache:
            metrics_data['cache_stats'] = self.cache.get_stats()

        return metrics_data

    def clear_cache(self):
        """清空缓存"""
        if self.cache:
            self.cache.clear()
            logger.info("缓存已清空")

    def reset_metrics(self):
        """重置性能指标"""
        self.metrics = PerformanceMetrics()
        logger.info("性能指标已重置")

    # 以下是原始技能的方法，保持向后兼容
    def _load_embedded_roles(self) -> Dict[str, Any]:
        """加载嵌入的角色配置"""
        return {
            'default': {
                'name': 'Default',
                'system_prompt': '你是一个帮助完成心理测评的AI助手。请根据问题给出真实、自然的回答。',
                'personality_traits': {}
            },
            'intj': {
                'name': 'INTJ - 建筑师',
                'system_prompt': '你是一个INTJ类型的人。你理性、独立、有远见，喜欢复杂的想法和战略规划。',
                'personality_traits': {
                    'openness': 0.9,
                    'conscientiousness': 0.8,
                    'extraversion': 0.2,
                    'agreeableness': 0.3,
                    'neuroticism': 0.4
                }
            },
            'enfj': {
                'name': 'ENFJ - 主人公',
                'system_prompt': '你是一个ENFJ类型的人。你热情、利他、有魅力，喜欢帮助他人实现潜能。',
                'personality_traits': {
                    'openness': 0.8,
                    'conscientiousness': 0.7,
                    'extraversion': 0.9,
                    'agreeableness': 0.9,
                    'neuroticism': 0.5
                }
            }
        }

    def _load_embedded_questionnaires(self) -> Dict[str, Any]:
        """加载嵌入的问卷数据"""
        return {
            'big_five_complete': {
                'name': 'Big Five 完整问卷',
                'description': '包含50个题目的完整大五人格问卷',
                'dimensions': ['E', 'A', 'C', 'N', 'O'],
                'questions': [
                    {
                        'question_id': 1,
                        'dimension': 'E',
                        'question': '我喜欢成为众人关注的焦点'
                    },
                    {
                        'question_id': 2,
                        'dimension': 'A',
                        'question': '我对他人的感受很敏感'
                    },
                    {
                        'question_id': 3,
                        'dimension': 'C',
                        'question': '我总是做好准备'
                    },
                    {
                        'question_id': 4,
                        'dimension': 'N',
                        'question': '我经常感到担心'
                    },
                    {
                        'question_id': 5,
                        'dimension': 'O',
                        'question': '我有丰富的想象力'
                    }
                    # 这里应该包含完整的50个题目，为简化示例只列出5个
                ]
            }
        }

    def get_available_questionnaires(self) -> List[str]:
        """获取可用的问卷列表"""
        return list(self.embedded_questionnaires.keys())

    def get_available_roles(self) -> List[str]:
        """获取可用的角色列表"""
        return list(self.embedded_roles.keys())

    def get_questionnaire_info(self, questionnaire_name: str) -> Optional[Dict[str, Any]]:
        """获取问卷信息"""
        return self.embedded_questionnaires.get(questionnaire_name)

    def get_role_info(self, role_name: str) -> Optional[Dict[str, Any]]:
        """获取角色信息"""
        return self.embedded_roles.get(role_name.lower())


# 向后兼容性别名
StandaloneQuestionnaireSkill = StandaloneQuestionnaireSkillV2


# 导出接口
__all__ = [
    'StandaloneQuestionnaireSkillV2',
    'StandaloneQuestionnaireSkill',  # 向后兼容
    'QuestionnaireConfig',
    'PerformanceMetrics',
    'ResponseCache',
    'RateLimiter'
]


if __name__ == "__main__":
    # 简单测试
    async def test_skill():
        config = QuestionnaireConfig(
            max_questions=5,
            concurrent_requests=2,
            cache_enabled=True,
            timeout_seconds=30
        )

        skill = StandaloneQuestionnaireSkillV2(config)

        result = await skill.run_questionnaire_test_async(
            questionnaire_name='big_five_complete',
            role_name='intj',
            emotional_stress=0,
            cognitive_trap='',
            context_tokens=0,
            temperature=0.6,
            max_questions=3
        )

        print("测试结果:")
        print(f"成功: {result['success']}")
        print(f"题目数: {result['session_info']['total_questions']}")
        print(f"成功回答: {result['session_info']['successful_responses']}")

        if skill.config.enable_metrics:
            print("\n性能指标:")
            metrics = skill.get_metrics()
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")

    asyncio.run(test_skill())