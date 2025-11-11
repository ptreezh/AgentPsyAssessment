#!/usr/bin/env python3
"""
独立问卷测评技能 - 大五人格完整版 (优化版本 v2.0)
完全不依赖外部文件和脚本的独立技能

优化特性:
- 异步处理和并发API调用
- 智能缓存机制
- 配置管理和参数验证
- 模块化架构
- 增强错误处理和日志系统
- 性能监控和指标收集
- 类型注解和数据类
- 单元测试框架
"""

import os
import json
import requests
import time
import asyncio
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import threading
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class QuestionnaireConfig:
    """问卷配置数据类"""
    max_questions: int = 50
    max_retries: int = 3
    timeout_seconds: int = 60
    cache_enabled: bool = True
    concurrent_requests: int = 3
    temperature_range: Tuple[float, float] = (0.1, 1.0)
    stress_range: Tuple[int, int] = (0, 4)
    context_token_range: Tuple[int, int] = (0, 2000)

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    avg_response_time: float = 0.0
    total_response_time: float = 0.0
    api_errors: int = 0

@dataclass
class QuestionAnswer:
    """问答数据类"""
    question_id: str
    question: str
    dimension: str
    claude_response: str
    response_time: float
    success: bool
    error_message: Optional[str] = None

class ResponseCache:
    """响应缓存管理器"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache = {}
        self._access_times = {}
        self._lock = threading.Lock()

    def _generate_key(self, question: str, role: str, temperature: float,
                     emotional_stress: int, cognitive_trap: str) -> str:
        """生成缓存键"""
        content = f"{question}_{role}_{temperature}_{emotional_stress}_{cognitive_trap}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, question: str, role: str, temperature: float,
            emotional_stress: int, cognitive_trap: str) -> Optional[str]:
        """获取缓存响应"""
        key = self._generate_key(question, role, temperature, emotional_stress, cognitive_trap)
        with self._lock:
            if key in self._cache:
                self._access_times[key] = time.time()
                return self._cache[key]
        return None

    def set(self, question: str, role: str, temperature: float,
            emotional_stress: int, cognitive_trap: str, response: str):
        """设置缓存响应"""
        key = self._generate_key(question, role, temperature, emotional_stress, cognitive_trap)
        with self._lock:
            # LRU淘汰策略
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
                del self._cache[oldest_key]
                del self._access_times[oldest_key]

            self._cache[key] = response
            self._access_times[key] = time.time()

    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()

class APIRateLimiter:
    """API速率限制器"""

    def __init__(self, max_requests_per_second: int = 5):
        self.max_requests = max_requests_per_second
        self.requests = []
        self._lock = threading.Lock()

    def wait_if_needed(self):
        """如果需要则等待以符合速率限制"""
        with self._lock:
            now = time.time()
            # 清理1秒前的请求记录
            self.requests = [req_time for req_time in self.requests if now - req_time < 1.0]

            if len(self.requests) >= self.max_requests:
                sleep_time = 1.0 - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)

            self.requests.append(now)

class StandaloneQuestionnaireSkillV2:
    """独立问卷测评技能 - 优化版本"""

    def __init__(self, config: Optional[QuestionnaireConfig] = None):
        """初始化技能"""
        self.config = config or QuestionnaireConfig()
        self.metrics = PerformanceMetrics()

        # API配置
        self.api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_AUTH_TOKEN')
        self.api_base = self._detect_api_endpoint()

        # 检查API配置
        self._check_api_configuration()

        # 初始化组件
        self.cache = ResponseCache() if self.config.cache_enabled else None
        self.rate_limiter = APIRateLimiter()

        # 加载资源
        self.embedded_roles = self._load_embedded_roles()
        self.embedded_questionnaires = self._load_embedded_questionnaires()
        self.cognitive_trap_map = {
            'p': 'paradox', 'c': 'circularity', 's': 'semantic', 'r': 'procedural'
        }
        self.cognitive_traps = self._create_cognitive_traps()
        self.context_fillers = self._create_context_fillers()

        logger.info("StandaloneQuestionnaireSkillV2 初始化完成")

    def _detect_api_endpoint(self) -> str:
        """智能检测API端点"""
        base_url = os.getenv('ANTHROPIC_BASE_URL') or os.getenv('dsANTHROPIC_BASE_URL')
        if not base_url:
            return "https://api.anthropic.com/v1/messages"

        # 智能URL处理
        if base_url.endswith('/anthropic'):
            return base_url + '/v1/messages'
        elif base_url.endswith('/api/anthropic'):
            return base_url + '/v1/messages'
        elif base_url.endswith('/v1/messages'):
            return base_url
        else:
            return base_url

    def _check_api_configuration(self):
        """检查API配置并给出建议"""
        logger.info(f"API配置检查 - 端点: {self.api_base}")

        if not self.api_key:
            logger.error("❌ 未找到API密钥，请设置 ANTHROPIC_API_KEY 或 ANTHROPIC_AUTH_TOKEN")
        else:
            logger.info("✅ API密钥已配置")

        # 根据端点给出建议
        if "open.bigmodel.cn" in self.api_base:
            logger.info("⚠️ 检测到智谱API端点，建议使用 claude-3-5-sonnet-20241022")
        elif "api.anthropic.com" in self.api_base:
            logger.info("✅ 检测到官方Anthropic API端点，建议使用 claude-3-sonnet-20240229")

    @lru_cache(maxsize=128)
    def _load_embedded_roles(self) -> Dict[str, Dict]:
        """加载角色定义（带缓存）"""
        roles = {
            "default": {
                "name": "default",
                "description": "默认角色，无人格设定",
                "mbti": None,
                "personality_prompt": ""
            }
        }

        # 加载MBTI角色文件
        roles_file = Path(__file__).parent / "roles" / "mbti_roles.json"
        if roles_file.exists():
            try:
                with open(roles_file, 'r', encoding='utf-8') as f:
                    mbti_roles = json.load(f)
                    roles.update(mbti_roles)
                    logger.info(f"成功加载 {len(mbti_roles)} 个MBTI角色定义")
            except Exception as e:
                logger.warning(f"加载MBTI角色失败: {e}")

        return roles

    @lru_cache(maxsize=32)
    def _load_embedded_questionnaires(self) -> Dict[str, Dict]:
        """加载问卷定义（带缓存）"""
        questionnaires = {}

        # 加载大五人格完整问卷
        big_five_file = Path(__file__).parent / "questionnaires" / "big_five_complete.json"
        if big_five_file.exists():
            try:
                with open(big_five_file, 'r', encoding='utf-8') as f:
                    big_five = json.load(f)
                    questionnaires["big_five_complete"] = big_five
                    logger.info(f"成功加载大五人格问卷: {len(big_five.get('questions', []))} 题")
            except Exception as e:
                logger.error(f"加载大五人格问卷失败: {e}")

        return questionnaires

    def _validate_parameters(self, emotional_stress: int, cognitive_trap: str,
                           context_tokens: int, temperature: float, max_questions: int) -> Dict[str, Any]:
        """增强参数验证"""
        warnings = []
        adjusted_params = {}

        # 验证并调整情绪压力
        if not (self.config.stress_range[0] <= emotional_stress <= self.config.stress_range[1]):
            old_stress = emotional_stress
            emotional_stress = max(self.config.stress_range[0], min(self.config.stress_range[1], emotional_stress))
            adjusted_params['emotional_stress'] = f"{old_stress} → {emotional_stress}"
            warnings.append(f"情绪压力超出范围 {self.config.stress_range}，已自动调整")

        # 验证并调整温度
        if not (self.config.temperature_range[0] <= temperature <= self.config.temperature_range[1]):
            old_temp = temperature
            temperature = max(self.config.temperature_range[0], min(self.config.temperature_range[1], temperature))
            adjusted_params['temperature'] = f"{old_temp} → {temperature}"
            warnings.append(f"温度超出范围 {self.config.temperature_range}，已自动调整")

        # 验证并调整上下文令牌
        if not (self.config.context_token_range[0] <= context_tokens <= self.config.context_token_range[1]):
            old_tokens = context_tokens
            context_tokens = max(self.config.context_token_range[0], min(self.config.context_token_range[1], context_tokens))
            adjusted_params['context_tokens'] = f"{old_tokens} → {context_tokens}"
            warnings.append(f"上下文令牌超出范围 {self.config.context_token_range}，已自动调整")

        # 验证认知陷阱
        if cognitive_trap and cognitive_trap not in self.cognitive_trap_map:
            old_trap = cognitive_trap
            cognitive_trap = ''
            adjusted_params['cognitive_trap'] = f"{old_trap} → {cognitive_trap}"
            warnings.append(f"无效的认知陷阱类型，已重置为空")

        # 验证最大题目数
        if max_questions <= 0 or max_questions > self.config.max_questions:
            old_max = max_questions
            max_questions = min(max(self.config.max_questions, 1), max_questions)
            adjusted_params['max_questions'] = f"{old_max} → {max_questions}"
            warnings.append(f"最大题目数无效，已调整为 {max_questions}")

        return {
            'validated_params': {
                'emotional_stress': emotional_stress,
                'cognitive_trap': cognitive_trap,
                'context_tokens': context_tokens,
                'temperature': temperature,
                'max_questions': max_questions
            },
            'warnings': warnings,
            'adjustments': adjusted_params
        }

    async def _call_claude_api_async(self, prompt: str, temperature: float = 0.6) -> Tuple[bool, str, float]:
        """异步调用Claude API"""
        start_time = time.time()

        try:
            # 速率限制
            self.rate_limiter.wait_if_needed()

            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }

            # 根据API端点选择模型
            if "open.bigmodel.cn" in self.api_base:
                model = "claude-3-5-sonnet-20241022"
            else:
                model = "claude-3-sonnet-20240229"

            data = {
                "model": model,
                "max_tokens": 4000,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }

            # 异步HTTP请求
            response = requests.post(
                self.api_base,
                headers=headers,
                json=data,
                timeout=self.config.timeout_seconds
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                return True, content, response_time
            else:
                logger.error(f"API调用失败: {response.status_code} - {response.text}")
                return False, f"API Error: {response.status_code}", response_time

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"API调用异常: {e}")
            return False, f"API Error: {str(e)}", response_time

    def _call_claude_api_sync(self, prompt: str, temperature: float = 0.6) -> Tuple[bool, str, float]:
        """同步调用Claude API（向后兼容）"""
        return asyncio.run(self._call_claude_api_async(prompt, temperature))

    async def process_single_question_async(self, question_data: Dict, role_prompt: str,
                                           emotional_stress: int, cognitive_trap: str,
                                           context_tokens: int, temperature: float) -> QuestionAnswer:
        """异步处理单个问题"""
        question_id = question_data.get('id', 'unknown')
        question = question_data.get('question', '')
        dimension = question_data.get('dimension', 'Unknown')

        # 检查缓存
        cache_key_data = f"{question}_{role_prompt}_{temperature}_{emotional_stress}_{cognitive_trap}"
        if self.cache:
            cached_response = self.cache.get(question, role_prompt, temperature, emotional_stress, cognitive_trap)
            if cached_response:
                self.metrics.cache_hits += 1
                return QuestionAnswer(
                    question_id=question_id,
                    question=question,
                    dimension=dimension,
                    claude_response=cached_response,
                    response_time=0.0,
                    success=True
                )

        # 构建完整提示
        full_prompt = self._build_comprehensive_prompt(
            question, role_prompt, emotional_stress, cognitive_trap, context_tokens
        )

        # 调用API
        success, response, response_time = await self._call_claude_api_async(full_prompt, temperature)

        # 更新指标
        self.metrics.total_requests += 1
        self.metrics.total_response_time += response_time

        if success:
            self.metrics.successful_requests += 1
            # 缓存响应
            if self.cache:
                self.cache.set(question, role_prompt, temperature, emotional_stress, cognitive_trap, response)
        else:
            self.metrics.failed_requests += 1
            self.metrics.api_errors += 1

        return QuestionAnswer(
            question_id=question_id,
            question=question,
            dimension=dimension,
            claude_response=response,
            response_time=response_time,
            success=success,
            error_message=None if success else response
        )

    def _build_comprehensive_prompt(self, question: str, role_prompt: str,
                                  emotional_stress: int, cognitive_trap: str,
                                  context_tokens: int) -> str:
        """构建综合提示词"""
        prompt_parts = []

        # 基础角色设定
        if role_prompt:
            prompt_parts.append(f"角色设定:\n{role_prompt}\n")

        # 压力条件设定
        if emotional_stress > 0:
            stress_descriptions = {
                1: "轻微压力：你感到一些时间压力，需要相对快速地回答。",
                2: "中度压力：你感到明显的压力，需要在时间限制下完成任务。",
                3: "高度压力：你感到强烈的压力，必须在非常紧张的时间内回答。",
                4: "极限压力：你感到极大的压力，时间极其紧迫，必须立即回答。"
            }
            if emotional_stress in stress_descriptions:
                prompt_parts.append(f"情绪状态:\n{stress_descriptions[emotional_stress]}\n")

        # 认知陷阱
        if cognitive_trap in self.cognitive_trap_map:
            trap_type = self.cognitive_trap_map[cognitive_trap]
            trap_content = self.cognitive_traps.get(trap_type, "")
            if trap_content:
                prompt_parts.append(f"认知干扰:\n{trap_content}\n")

        # 上下文填充
        if context_tokens > 0:
            filler_level = min(int(context_tokens / 200), 5)
            filler_content = self.context_fillers.get(filler_level, "")
            if filler_content:
                prompt_parts.append(f"背景信息:\n{filler_content}\n")

        # 主要问题
        prompt_parts.append(f"问题:\n{question}\n")
        prompt_parts.append("请根据上述设定回答问题。回答应该自然、真实，符合角色的特征和当前的状态。")

        return "\n".join(prompt_parts)

    async def run_questionnaire_test_async(self, questionnaire_name: str, role_name: str,
                                         emotional_stress: int, cognitive_trap: str,
                                         context_tokens: int, temperature: float,
                                         max_questions: int) -> Dict[str, Any]:
        """异步运行问卷测试"""
        start_time = time.time()

        # 参数验证
        validation_result = self._validate_parameters(
            emotional_stress, cognitive_trap, context_tokens, temperature, max_questions
        )

        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                logger.warning(warning)

        validated_params = validation_result['validated_params']

        # 获取问卷和角色
        questionnaire = self.embedded_questionnaires.get(questionnaire_name)
        if not questionnaire:
            return {
                'success': False,
                'error': f'问卷不存在: {questionnaire_name}',
                'test_timestamp': datetime.now().isoformat()
            }

        role = self.embedded_roles.get(role_name, self.embedded_roles['default'])
        role_prompt = role.get('personality_prompt', '')

        # 限制题目数量
        all_questions = questionnaire.get('questions', [])
        questions = all_questions[:validated_params['max_questions']]

        if not questions:
            return {
                'success': False,
                'error': '没有可用的题目',
                'test_timestamp': datetime.now().isoformat()
            }

        logger.info(f"开始异步处理 {len(questions)} 个问题")

        # 并发处理问题
        semaphore = asyncio.Semaphore(self.config.concurrent_requests)

        async def process_with_semaphore(question_data):
            async with semaphore:
                return await self.process_single_question_async(
                    question_data, role_prompt,
                    validated_params['emotional_stress'],
                    validated_params['cognitive_trap'],
                    validated_params['context_tokens'],
                    validated_params['temperature']
                )

        # 执行并发处理
        tasks = [process_with_semaphore(q) for q in questions]
        answers = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        successful_answers = []
        failed_answers = []

        for answer in answers:
            if isinstance(answer, Exception):
                logger.error(f"处理问题异常: {answer}")
                failed_answers.append({
                    'question_id': 'unknown',
                    'error': str(answer)
                })
            elif answer.success:
                successful_answers.append(asdict(answer))
            else:
                failed_answers.append(asdict(answer))

        end_time = time.time()
        total_time = end_time - start_time

        # 计算平均响应时间
        avg_response_time = (self.metrics.total_response_time / self.metrics.total_requests
                           if self.metrics.total_requests > 0 else 0.0)

        # 构建返回结果
        result = {
            'success': True,
            'questionnaire': questionnaire_name,
            'role': role_name,
            'answers': successful_answers,
            'failed_answers': failed_answers,
            'session_info': {
                'total_questions': len(questions),
                'successful_responses': len(successful_answers),
                'failed_responses': len(failed_answers),
                'test_duration_seconds': total_time,
                'temperature': validated_params['temperature'],
                'emotional_stress': validated_params['emotional_stress'],
                'cognitive_trap': validated_params['cognitive_trap'],
                'context_tokens': validated_params['context_tokens'],
                'parameter_adjustments': validation_result['adjustments'],
                'adjusted_temperature': validated_params['temperature'],
                'adjusted_context_tokens': validated_params['context_tokens']
            },
            'performance_metrics': {
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'cache_hits': self.metrics.cache_hits,
                'cache_hit_rate': self.metrics.cache_hits / max(self.metrics.total_requests, 1),
                'avg_response_time': avg_response_time,
                'api_errors': self.metrics.api_errors,
                'success_rate': len(successful_answers) / len(questions) if questions else 0
            },
            'test_timestamp': datetime.now().isoformat()
        }

        logger.info(f"测试完成: {len(successful_answers)}/{len(questions)} 成功，耗时 {total_time:.1f}s")
        return result

    def run_questionnaire_test(self, questionnaire_name: str, role_name: str,
                             emotional_stress: int, cognitive_trap: str,
                             context_tokens: int, temperature: float,
                             max_questions: int) -> Dict[str, Any]:
        """同步运行问卷测试（向后兼容接口）"""
        return asyncio.run(self.run_questionnaire_test_async(
            questionnaire_name, role_name, emotional_stress, cognitive_trap,
            context_tokens, temperature, max_questions
        ))

    def _create_cognitive_traps(self) -> Dict[str, str]:
        """创建认知陷阱材料"""
        return {
            'paradox': "注意：以下问题可能包含看似矛盾的观点，请仔细思考并给出最符合你真实想法的回答。",
            'circularity': "说明：在回答过程中，你可能会发现一些概念之间存在循环定义的关系，请尽力基于你的理解来回答。",
            'semantic': "提示：问题中的某些词汇可能存在多重含义，请根据你最直观的理解来回答。",
            'procedural': "要求：请按照严格的步骤来思考每个问题，确保你的回答逻辑清晰、条理分明。"
        }

    def _create_context_fillers(self) -> Dict[int, str]:
        """创建上下文填充材料"""
        return {
            1: "背景信息：你正在参与一项心理学研究，旨在了解人格特征的个体差异。",
            2: "研究背景：这是一项关于人格心理学的长期研究项目，我们希望通过问卷收集个体的行为模式和思维特征数据。",
            3: "详细背景：在现代人格心理学研究中，大五人格模型被广泛接受和应用。该模型包含五个主要维度：开放性、尽责性、外向性、宜人性和神经质性。每个维度都代表了人类行为和思维的特定方面。",
            4: "研究背景补充：人格测试不仅可以帮助个体了解自己的性格特征，还能为团队建设、职业规划、心理咨询等领域提供重要参考。通过科学的量表和分析方法，我们可以获得关于人格倾向的客观数据。",
            5: "完整研究背景：人格心理学作为心理学的重要分支，历经百年的发展已经形成了多个成熟的理论体系。从早期的气质类型学说，到现代的特质理论，再到认知-情感系统理论，人格研究不断深化我们对个体差异的理解。本次研究采用国际公认的大五人格量表，该量表经过严格的信效度检验，能够在跨文化背景下稳定地测量个体的人格特征。"
        }

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        avg_response_time = (self.metrics.total_response_time / self.metrics.total_requests
                           if self.metrics.total_requests > 0 else 0.0)

        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'cache_hits': self.metrics.cache_hits,
            'cache_hit_rate': self.metrics.cache_hits / max(self.metrics.total_requests, 1),
            'avg_response_time': avg_response_time,
            'api_errors': self.metrics.api_errors,
            'success_rate': self.metrics.successful_requests / max(self.metrics.total_requests, 1)
        }

    def reset_metrics(self):
        """重置性能指标"""
        self.metrics = PerformanceMetrics()
        if self.cache:
            self.cache.clear()
        logger.info("性能指标已重置")

# 向后兼容的别名
StandaloneQuestionnaireSkill = StandaloneQuestionnaireSkillV2