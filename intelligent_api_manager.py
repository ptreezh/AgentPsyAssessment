#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能API密钥管理器 - 提供安全的API密钥轮换和管理机制
"""

import os
import json
import time
import random
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import requests
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIStatus(Enum):
    """API状态"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

@dataclass
class APIKey:
    """API密钥信息"""
    id: str
    key: str
    provider: str
    status: APIStatus
    created_at: datetime
    last_used: Optional[datetime] = None
    usage_count: int = 0
    error_count: int = 0
    rate_limit_reset_time: Optional[datetime] = None
    metadata: Dict = None

class IntelligentAPIManager:
    """智能API管理器"""

    def __init__(self, config_file: str = "api_keys_config.json"):
        self.config_file = config_file
        self.api_keys: Dict[str, APIKey] = {}
        self.current_index: Dict[str, int] = {}
        self.load_configuration()

    def load_configuration(self):
        """加载API密钥配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 从JSON恢复APIKey对象
                for provider, keys_data in data.get('providers', {}).items():
                    self.api_keys[provider] = []
                    self.current_index[provider] = 0

                    for key_data in keys_data:
                        api_key = APIKey(
                            id=key_data['id'],
                            key=key_data['key'],
                            provider=key_data['provider'],
                            status=APIStatus(key_data['status']),
                            created_at=datetime.fromisoformat(key_data['created_at']),
                            last_used=datetime.fromisoformat(key_data['last_used']) if key_data.get('last_used') else None,
                            usage_count=key_data['usage_count'],
                            error_count=key_data['error_count'],
                            rate_limit_reset_time=datetime.fromisoformat(key_data['rate_limit_reset_time']) if key_data.get('rate_limit_reset_time') else None,
                            metadata=key_data.get('metadata', {})
                        )
                        self.api_keys[provider].append(api_key)

                logger.info(f"从配置文件加载了 {sum(len(keys) for keys in self.api_keys.values())} 个API密钥")
            else:
                logger.info("配置文件不存在，创建默认配置")
                self._create_default_configuration()

        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._create_default_configuration()

    def _create_default_configuration(self):
        """创建默认配置"""
        # 从环境变量加载API密钥
        env_keys = self._load_from_environment()

        if not env_keys:
            logger.warning("未找到环境变量中的API密钥")
            return

        # 将环境变量转换为APIKey对象
        for provider, keys in env_keys.items():
            self.api_keys[provider] = []
            self.current_index[provider] = 0

            for i, key in enumerate(keys):
                api_key = APIKey(
                    id=f"{provider}_key_{i}",
                    key=key,
                    provider=provider,
                    status=APIStatus.ACTIVE,
                    created_at=datetime.now(),
                    metadata={'source': 'environment'}
                )
                self.api_keys[provider].append(api_key)

        self.save_configuration()

    def _load_from_environment(self) -> Dict[str, List[str]]:
        """从环境变量加载API密钥"""
        env_keys = {}

        # OpenRouter API
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key:
            env_keys['openrouter'] = [openrouter_key]

        # DashScope API
        dashscope_key = os.getenv('DASHSCOPE_API_KEY')
        if dashscope_key:
            env_keys['dashscope'] = [dashscope_key]

        # DeepSeek API
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            env_keys['deepseek'] = [deepseek_key]

        # GLM API
        glm_key = os.getenv('GLM_API_KEY')
        if glm_key:
            env_keys['glm'] = [glm_key]

        # Moonshot API
        moonshot_key = os.getenv('MOONSHOT_API_KEY')
        if moonshot_key:
            env_keys['moonshot'] = [moonshot_key]

        return env_keys

    def save_configuration(self):
        """保存配置到文件"""
        try:
            # 创建配置目录
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            # 转换为可序列化的格式
            config_data = {
                'providers': {}
            }

            for provider, keys in self.api_keys.items():
                config_data['providers'][provider] = []
                for api_key in keys:
                    config_data['providers'][provider].append({
                        'id': api_key.id,
                        'key': api_key.key,  # 在实际部署时应该加密
                        'provider': api_key.provider,
                        'status': api_key.status.value,
                        'created_at': api_key.created_at.isoformat(),
                        'last_used': api_key.last_used.isoformat() if api_key.last_used else None,
                        'usage_count': api_key.usage_count,
                        'error_count': api_key.error_count,
                        'rate_limit_reset_time': api_key.rate_limit_reset_time.isoformat() if api_key.rate_limit_reset_time else None,
                        'metadata': api_key.metadata or {}
                    })

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            logger.info(f"配置已保存到: {self.config_file}")

        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def get_available_key(self, provider: str) -> Optional[APIKey]:
        """获取可用的API密钥"""
        if provider not in self.api_keys or not self.api_keys[provider]:
            logger.warning(f"未找到提供商 {provider} 的API密钥")
            return None

        # 清理过期的速率限制
        self._cleanup_expired_rate_limits(provider)

        # 获取可用的密钥
        available_keys = [
            key for key in self.api_keys[provider]
            if key.status == APIStatus.ACTIVE
        ]

        if not available_keys:
            # 如果没有可用的密钥，尝试恢复降级的密钥
            degraded_keys = [
                key for key in self.api_keys[provider]
                if key.status == APIStatus.DEGRADED
            ]
            if degraded_keys:
                # 恢复第一个降级的密钥
                degraded_keys[0].status = APIStatus.ACTIVE
                available_keys = degraded_keys
                logger.info(f"恢复降级密钥: {degraded_keys[0].id}")

        if not available_keys:
            logger.error(f"提供商 {provider} 没有可用的API密钥")
            return None

        # 选择使用次数最少的密钥（负载均衡）
        selected_key = min(available_keys, key=lambda k: k.usage_count)

        # 更新使用记录
        selected_key.last_used = datetime.now()
        selected_key.usage_count += 1

        return selected_key

    def mark_key_error(self, provider: str, key_id: str, error_message: str):
        """标记密钥错误"""
        if provider not in self.api_keys:
            return

        for api_key in self.api_keys[provider]:
            if api_key.id == key_id:
                api_key.error_count += 1

                # 检查错误类型
                error_lower = error_message.lower()
                if any(keyword in error_lower for keyword in [
                    'rate limit', '429', 'too many requests', 'quota'
                ]):
                    api_key.status = APIStatus.RATE_LIMITED
                    api_key.rate_limit_reset_time = datetime.now() + timedelta(hours=1)
                    logger.warning(f"API密钥 {key_id} 触发速率限制")

                elif api_key.error_count >= 5:
                    api_key.status = APIStatus.FAILED
                    logger.error(f"API密钥 {key_id} 标记为失败 (错误次数: {api_key.error_count})")

                elif api_key.error_count >= 2:
                    api_key.status = APIStatus.DEGRADED
                    logger.warning(f"API密钥 {key_id} 降级 (错误次数: {api_key.error_count})")

                break

    def _cleanup_expired_rate_limits(self, provider: str):
        """清理过期的速率限制"""
        if provider not in self.api_keys:
            return

        current_time = datetime.now()
        for api_key in self.api_keys[provider]:
            if (api_key.status == APIStatus.RATE_LIMITED and
                api_key.rate_limit_reset_time and
                current_time >= api_key.rate_limit_reset_time):
                api_key.status = APIStatus.ACTIVE
                api_key.rate_limit_reset_time = None
                logger.info(f"API密钥 {api_key.id} 速率限制已解除")

    def add_api_key(self, provider: str, key: str, metadata: Dict = None) -> str:
        """添加新的API密钥"""
        if provider not in self.api_keys:
            self.api_keys[provider] = []
            self.current_index[provider] = 0

        api_key = APIKey(
            id=f"{provider}_key_{int(time.time())}_{random.randint(1000, 9999)}",
            key=key,
            provider=provider,
            status=APIStatus.ACTIVE,
            created_at=datetime.now(),
            metadata=metadata or {}
        )

        self.api_keys[provider].append(api_key)
        self.save_configuration()

        logger.info(f"添加新API密钥: {api_key.id}")
        return api_key.id

    def remove_api_key(self, provider: str, key_id: str) -> bool:
        """移除API密钥"""
        if provider not in self.api_keys:
            return False

        original_count = len(self.api_keys[provider])
        self.api_keys[provider] = [
            key for key in self.api_keys[provider]
            if key.id != key_id
        ]

        if len(self.api_keys[provider]) < original_count:
            self.save_configuration()
            logger.info(f"移除API密钥: {key_id}")
            return True

        return False

    def rotate_keys(self, provider: str) -> bool:
        """轮换API密钥"""
        if provider not in self.api_keys or len(self.api_keys[provider]) < 2:
            logger.warning(f"提供商 {provider} 密钥数量不足，无法轮换")
            return False

        # 将当前密钥状态降级，激活下一个密钥
        current_index = self.current_index[provider]
        current_key = self.api_keys[provider][current_index]

        # 标记当前密钥为降级
        current_key.status = APIStatus.DEGRADED
        current_key.error_count = 0  # 重置错误计数

        # 切换到下一个密钥
        next_index = (current_index + 1) % len(self.api_keys[provider])
        self.current_index[provider] = next_index
        next_key = self.api_keys[provider][next_index]
        next_key.status = APIStatus.ACTIVE

        self.save_configuration()

        logger.info(f"API密钥轮换: {current_key.id} -> {next_key.id}")
        return True

    def get_status_report(self) -> Dict:
        """获取状态报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'providers': {}
        }

        for provider, keys in self.api_keys.items():
            status_counts = {status.value: 0 for status in APIStatus}
            total_usage = sum(key.usage_count for key in keys)
            total_errors = sum(key.error_count for key in keys)

            for key in keys:
                status_counts[key.status.value] += 1

            report['providers'][provider] = {
                'total_keys': len(keys),
                'status_distribution': status_counts,
                'total_usage': total_usage,
                'total_errors': total_errors,
                'keys': [
                    {
                        'id': key.id,
                        'status': key.status.value,
                        'usage_count': key.usage_count,
                        'error_count': key.error_count,
                        'last_used': key.last_used.isoformat() if key.last_used else None,
                        'created_at': key.created_at.isoformat()
                    }
                    for key in keys
                ]
            }

        return report

    def validate_key(self, provider: str, api_url: str, headers: Dict) -> bool:
        """验证API密钥是否有效"""
        key = self.get_available_key(provider)
        if not key:
            return False

        try:
            # 发送测试请求
            test_response = requests.get(
                api_url,
                headers={**headers, 'Authorization': f'Bearer {key.key}'},
                timeout=10
            )

            if test_response.status_code in [200, 201]:
                logger.info(f"API密钥 {key.id} 验证成功")
                return True
            else:
                logger.warning(f"API密钥 {key.id} 验证失败: HTTP {test_response.status_code}")
                self.mark_key_error(provider, key.id, f"HTTP {test_response.status_code}")
                return False

        except Exception as e:
            logger.error(f"API密钥验证异常: {e}")
            self.mark_key_error(provider, key.id, str(e))
            return False

# 全局API管理器实例
global_api_manager = IntelligentAPIManager()

def get_api_key(provider: str) -> Optional[str]:
    """获取API密钥的便捷函数"""
    key = global_api_manager.get_available_key(provider)
    return key.key if key else None

def mark_api_error(provider: str, key_id: str, error_message: str):
    """标记API错误的便捷函数"""
    global_api_manager.mark_key_error(provider, key_id, error_message)

if __name__ == "__main__":
    # 测试API管理器
    print("🧪 测试智能API管理器")

    # 显示状态报告
    report = global_api_manager.get_status_report()
    print(f"📊 API状态报告:")
    for provider, info in report['providers'].items():
        print(f"   {provider}: {info['total_keys']} 个密钥, {info['total_usage']} 次使用, {info['total_errors']} 次错误")
        print(f"     状态分布: {info['status_distribution']}")

    # 测试获取API密钥
    test_key = get_api_key('openrouter')
    if test_key:
        print(f"✅ 获取到OpenRouter API密钥: {test_key[:20]}...")
    else:
        print("❌ 未找到OpenRouter API密钥")