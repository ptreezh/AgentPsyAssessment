#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能错误处理器 - 提供全面的错误处理和恢复机制
"""

import time
import random
import logging
from typing import Callable, Any, Dict, Optional, Union
from functools import wraps
import traceback
from enum import Enum
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """错误类别"""
    NETWORK = "network"
    API_LIMIT = "api_limit"
    JSON_PARSE = "json_parse"
    SYSTEM = "system"
    DATA = "data"
    UNKNOWN = "unknown"

class RetryConfig:
    """重试配置"""
    def __init__(self,
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class ErrorClassifier:
    """错误分类器"""

    @staticmethod
    def classify_error(error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """分类错误"""
        error_str = str(error).lower()
        error_type = type(error).__name__

        # 网络相关错误
        if any(keyword in error_str for keyword in [
            'connection', 'timeout', 'network', 'dns', 'socket',
            'connectionreset', 'connection aborted', 'eof'
        ]):
            return ErrorCategory.NETWORK, ErrorSeverity.HIGH

        # API限制错误
        if any(keyword in error_str for keyword in [
            '429', 'rate limit', 'too many requests', 'quota',
            '402', 'payment required', 'usage limit'
        ]):
            return ErrorCategory.API_LIMIT, ErrorSeverity.MEDIUM

        # JSON解析错误
        if any(keyword in error_str for keyword in [
            'json', 'parse', 'decode', 'encoding', 'syntax'
        ]) or error_type in ['JSONDecodeError']:
            return ErrorCategory.JSON_PARSE, ErrorSeverity.LOW

        # 系统错误
        if any(keyword in error_str for keyword in [
            'memory', 'disk', 'permission', 'file not found',
            'oserror', 'permission denied'
        ]):
            return ErrorCategory.SYSTEM, ErrorSeverity.HIGH

        # 数据错误
        if any(keyword in error_str for keyword in [
            'type', 'value', 'attribute', 'key', 'index'
        ]):
            return ErrorCategory.DATA, ErrorSeverity.LOW

        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM

class CircuitBreaker:
    """断路器模式"""

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                    logger.info("断路器状态: OPEN -> HALF_OPEN")
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置断路器"""
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout

    def _on_success(self):
        """成功时重置状态"""
        self.failure_count = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            logger.info("断路器状态: HALF_OPEN -> CLOSED")

    def _on_failure(self):
        """失败时更新状态"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"断路器状态: CLOSE -> OPEN (失败次数: {self.failure_count})")

class RateLimiter:
    """智能限流器"""

    def __init__(self, max_requests: int = 10, time_window: float = 60.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def is_allowed(self) -> bool:
        """检查是否允许请求"""
        now = time.time()

        # 清理过期的请求记录
        self.requests = [req_time for req_time in self.requests
                        if now - req_time < self.time_window]

        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(now)
        return True

    def wait_time(self) -> float:
        """计算需要等待的时间"""
        if not self.requests:
            return 0.0

        oldest_request = min(self.requests)
        return max(0.0, self.time_window - (time.time() - oldest_request))

class IntelligentErrorHandler:
    """智能错误处理器"""

    def __init__(self):
        self.retry_configs = {
            ErrorCategory.NETWORK: RetryConfig(max_attempts=5, base_delay=2.0, max_delay=60.0),
            ErrorCategory.API_LIMIT: RetryConfig(max_attempts=3, base_delay=10.0, max_delay=300.0),
            ErrorCategory.JSON_PARSE: RetryConfig(max_attempts=2, base_delay=0.5, max_delay=5.0),
            ErrorCategory.SYSTEM: RetryConfig(max_attempts=1, base_delay=1.0, max_delay=10.0),
            ErrorCategory.DATA: RetryConfig(max_attempts=1, base_delay=0.1, max_delay=1.0),
            ErrorCategory.UNKNOWN: RetryConfig(max_attempts=3, base_delay=1.0, max_delay=30.0)
        }

        self.circuit_breakers = {}
        self.rate_limiters = {}
        self.error_stats = {}

    def handle_with_retry(self,
                         error_category: Optional[ErrorCategory] = None,
                         custom_config: Optional[RetryConfig] = None) -> Callable:
        """带重试的装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                config = custom_config or self.retry_configs.get(error_category or ErrorCategory.UNKNOWN)

                for attempt in range(config.max_attempts):
                    try:
                        return func(*args, **kwargs)

                    except Exception as e:
                        category, severity = ErrorClassifier.classify_error(e)

                        # 记录错误统计
                        self._record_error(category, str(e))

                        # 检查断路器
                        circuit_breaker = self._get_circuit_breaker(func.__name__)
                        if circuit_breaker.state == 'OPEN':
                            logger.error(f"断路器开启，跳过重试: {func.__name__}")
                            raise

                        # 检查是否应该重试
                        if attempt == config.max_attempts - 1:
                            logger.error(f"达到最大重试次数: {func.__name__} ({config.max_attempts}次)")
                            raise

                        # 计算延迟时间
                        delay = self._calculate_delay(attempt, config)
                        logger.warning(f"第{attempt + 1}次重试 {func.__name__}，延迟{delay:.2f}秒: {e}")
                        time.sleep(delay)

                # 不应该到达这里
                raise Exception(f"重试失败: {func.__name__}")

            return wrapper
        return decorator

    def _get_circuit_breaker(self, func_name: str) -> CircuitBreaker:
        """获取或创建断路器"""
        if func_name not in self.circuit_breakers:
            self.circuit_breakers[func_name] = CircuitBreaker()
        return self.circuit_breakers[func_name]

    def _get_rate_limiter(self, func_name: str) -> RateLimiter:
        """获取或创建限流器"""
        if func_name not in self.rate_limiters:
            # 根据函数类型设置不同的限流参数
            if 'ollama' in func_name.lower():
                self.rate_limiters[func_name] = RateLimiter(max_requests=5, time_window=60.0)
            elif 'cloud' in func_name.lower():
                self.rate_limiters[func_name] = RateLimiter(max_requests=10, time_window=60.0)
            else:
                self.rate_limiters[func_name] = RateLimiter(max_requests=20, time_window=60.0)

        return self.rate_limiters[func_name]

    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """计算重试延迟时间"""
        # 指数退避算法
        delay = config.base_delay * (config.exponential_base ** attempt)
        delay = min(delay, config.max_delay)

        # 添加抖动
        if config.jitter:
            jitter = delay * 0.1 * random.random()
            delay += jitter

        return delay

    def _record_error(self, category: ErrorCategory, error_message: str):
        """记录错误统计"""
        if category not in self.error_stats:
            self.error_stats[category] = {
                'count': 0,
                'first_occurrence': datetime.now(),
                'last_occurrence': datetime.now(),
                'messages': []
            }

        self.error_stats[category]['count'] += 1
        self.error_stats[category]['last_occurrence'] = datetime.now()

        # 只保留最近的消息（最多100条）
        messages = self.error_stats[category]['messages']
        messages.append(error_message)
        if len(messages) > 100:
            self.error_stats[category]['messages'] = messages[-100:]

    def apply_rate_limit(self, func_name: str) -> bool:
        """应用限流"""
        rate_limiter = self._get_rate_limiter(func_name)

        if not rate_limiter.is_allowed():
            wait_time = rate_limiter.wait_time()
            logger.info(f"限流生效，等待{wait_time:.2f}秒: {func_name}")
            time.sleep(wait_time)
            return False

        return True

    def get_error_report(self) -> Dict:
        """获取错误报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_errors': sum(stats['count'] for stats in self.error_stats.values()),
            'errors_by_category': {}
        }

        for category, stats in self.error_stats.items():
            report['errors_by_category'][category.value] = {
                'count': stats['count'],
                'first_occurrence': stats['first_occurrence'].isoformat(),
                'last_occurrence': stats['last_occurrence'].isoformat(),
                'recent_messages': stats['messages'][-5:]  # 最近5条消息
            }

        return report

# 全局错误处理器实例
global_error_handler = IntelligentErrorHandler()

def handle_errors(error_category: Optional[ErrorCategory] = None,
                  retry_config: Optional[RetryConfig] = None):
    """全局错误处理装饰器"""
    return global_error_handler.handle_with_retry(error_category, retry_config)

def apply_rate_limiting(func_name: str):
    """应用限流的装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            global_error_handler.apply_rate_limit(func_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # 测试错误处理器
    print("🧪 测试智能错误处理器")

    @handle_errors(ErrorCategory.NETWORK)
    def test_network_function():
        raise ConnectionError("模拟网络连接失败")

    @handle_errors(ErrorCategory.JSON_PARSE)
    def test_json_function():
        raise ValueError("模拟JSON解析失败")

    # 测试网络错误重试
    try:
        test_network_function()
    except Exception as e:
        print(f"✅ 网络错误处理测试: {type(e).__name__}")

    # 测试JSON错误重试
    try:
        test_json_function()
    except Exception as e:
        print(f"✅ JSON错误处理测试: {type(e).__name__}")

    # 显示错误报告
    report = global_error_handler.get_error_report()
    print(f"📊 错误报告: {report['total_errors']} 个错误")