#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弹性JSON序列化器 - 解决datetime对象序列化问题
"""

import json
import datetime
import uuid
import os
import time
import shutil
from decimal import Decimal
from typing import Any, Dict, Union
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilientJSONSerializer:
    """具有故障恢复能力的JSON序列化器"""

    def __init__(self):
        self.fallback_handlers = []
        self.setup_handlers()

    def setup_handlers(self):
        """设置多层序列化处理器"""
        # 处理器优先级从高到低
        self.fallback_handlers = [
            self._datetime_handler,
            self._decimal_handler,
            self._uuid_handler,
            self._set_handler,
            self._bytes_handler,
            self._object_handler,
            self._str_fallback_handler
        ]

    def serialize(self, obj: Any, indent: int = 2) -> str:
        """
        安全的JSON序列化，具有多级故障恢复能力

        Args:
            obj: 要序列化的对象
            indent: JSON缩进

        Returns:
            序列化后的JSON字符串
        """
        for attempt, handler in enumerate(self.fallback_handlers):
            try:
                return json.dumps(
                    obj,
                    default=handler,
                    ensure_ascii=False,
                    indent=indent,
                    separators=(',', ': ')
                )
            except (TypeError, ValueError) as e:
                logger.warning(f"JSON序列化尝试 {attempt + 1} 失败: {e}")
                if attempt == len(self.fallback_handlers) - 1:
                    # 最后的兜底策略
                    return self._emergency_serialize(obj)
                continue

        # 不应该到达这里
        return self._emergency_serialize(obj)

    def deserialize(self, json_str: str) -> Any:
        """
        安全的JSON反序列化

        Args:
            json_str: JSON字符串

        Returns:
            反序列化后的对象
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON反序列化失败: {e}")
            # 尝试修复常见的JSON问题
            return self._repair_and_deserialize(json_str)

    def _datetime_handler(self, obj: Any) -> Any:
        """处理datetime对象"""
        if isinstance(obj, datetime.datetime):
            return {
                '__type__': 'datetime',
                'value': obj.isoformat(),
                'timezone': obj.tzinfo.__class__.__name__ if obj.tzinfo else None
            }
        elif isinstance(obj, datetime.date):
            return {
                '__type__': 'date',
                'value': obj.isoformat()
            }
        elif isinstance(obj, datetime.time):
            return {
                '__type__': 'time',
                'value': obj.isoformat()
            }
        raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable by datetime handler')

    def _decimal_handler(self, obj: Any) -> Any:
        """处理Decimal对象"""
        if isinstance(obj, Decimal):
            return {
                '__type__': 'decimal',
                'value': str(obj)
            }
        raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable by decimal handler')

    def _uuid_handler(self, obj: Any) -> Any:
        """处理UUID对象"""
        if isinstance(obj, uuid.UUID):
            return {
                '__type__': 'uuid',
                'value': str(obj)
            }
        raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable by uuid handler')

    def _set_handler(self, obj: Any) -> Any:
        """处理set对象"""
        if isinstance(obj, set):
            return {
                '__type__': 'set',
                'value': list(obj)
            }
        raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable by set handler')

    def _bytes_handler(self, obj: Any) -> Any:
        """处理bytes对象"""
        if isinstance(obj, bytes):
            try:
                return {
                    '__type__': 'bytes',
                    'value': obj.decode('utf-8')
                }
            except UnicodeDecodeError:
                return {
                    '__type__': 'bytes_base64',
                    'value': obj.hex()
                }
        raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable by bytes handler')

    def _object_handler(self, obj: Any) -> Any:
        """处理一般对象"""
        if hasattr(obj, '__dict__'):
            # 尝试序列化对象的属性
            return {
                '__type__': 'object',
                'class': obj.__class__.__name__,
                'module': obj.__class__.__module__,
                'data': obj.__dict__
            }
        raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable by object handler')

    def _str_fallback_handler(self, obj: Any) -> str:
        """最终的字符串处理器"""
        return {
            '__type__': 'fallback',
            'value': str(obj),
            'original_type': type(obj).__name__
        }

    def _emergency_serialize(self, obj: Any) -> str:
        """紧急序列化策略"""
        logger.error("启用紧急JSON序列化策略")
        try:
            # 尝试最简单的序列化
            import pickle
            import base64

            # 使用pickle序列化，然后base64编码
            pickled = pickle.dumps(obj)
            encoded = base64.b64encode(pickled).decode('ascii')

            return json.dumps({
                '__emergency__': True,
                'data': encoded,
                'type': type(obj).__name__
            })

        except Exception as e:
            logger.error(f"紧急序列化也失败: {e}")
            # 最后的兜底：返回错误信息
            return json.dumps({
                '__error__': True,
                'message': f'Cannot serialize object of type {type(obj).__name__}: {str(e)}',
                'type': type(obj).__name__
            })

    def _repair_and_deserialize(self, json_str: str) -> Any:
        """修复JSON并反序列化"""
        # 常见的JSON问题修复
        try:
            # 移除可能的BOM
            if json_str.startswith('\ufeff'):
                json_str = json_str[1:]

            # 尝试直接解析
            return json.loads(json_str)

        except json.JSONDecodeError:
            # 尝试修复其他常见问题
            try:
                # 移除可能的控制字符
                import re
                cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                return json.loads(cleaned)
            except:
                # 如果还是失败，返回原始字符串
                return {'__parse_error__': True, 'data': json_str}

class EnhancedJSONFileHandler:
    """增强的JSON文件处理器"""

    def __init__(self, serializer: ResilientJSONSerializer = None):
        self.serializer = serializer or ResilientJSONSerializer()

    def save_json(self, data: Any, file_path: str, backup: bool = True) -> bool:
        """
        安全保存JSON文件

        Args:
            data: 要保存的数据
            file_path: 文件路径
            backup: 是否创建备份

        Returns:
            是否保存成功
        """
        try:
            # 创建备份
            if backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup_{int(time.time())}"
                shutil.copy2(file_path, backup_path)
                logger.info(f"创建备份文件: {backup_path}")

            # 序列化数据
            json_str = self.serializer.serialize(data)

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)

            logger.info(f"JSON文件保存成功: {file_path}")
            return True

        except Exception as e:
            logger.error(f"保存JSON文件失败 {file_path}: {e}")
            return False

    def load_json(self, file_path: str) -> Any:
        """
        安全加载JSON文件

        Args:
            file_path: 文件路径

        Returns:
            加载的数据，失败时返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()

            return self.serializer.deserialize(json_str)

        except Exception as e:
            logger.error(f"加载JSON文件失败 {file_path}: {e}")
            return None

# 全局序列化器实例
_global_serializer = ResilientJSONSerializer()

def safe_json_dumps(obj: Any, indent: int = 2) -> str:
    """全局安全JSON序列化函数"""
    return _global_serializer.serialize(obj, indent)

def safe_json_loads(json_str: str) -> Any:
    """全局安全JSON反序列化函数"""
    return _global_serializer.deserialize(json_str)

# 向后兼容的函数
def safe_json_handler(obj: Any) -> str:
    """兼容旧代码的JSON处理器"""
    return safe_json_dumps(obj)

if __name__ == "__main__":
    # 测试序列化器
    print("🧪 测试弹性JSON序列化器")

    test_data = {
        "datetime": datetime.datetime.now(),
        "date": datetime.date.today(),
        "set_data": {1, 2, 3},
        "uuid": uuid.uuid4(),
        "normal": "test",
        "number": 42
    }

    try:
        # 序列化
        json_str = safe_json_dumps(test_data)
        print("✅ 序列化成功")
        print(f"JSON长度: {len(json_str)} 字符")

        # 反序列化
        data = safe_json_loads(json_str)
        print("✅ 反序列化成功")
        print(f"数据类型: {type(data)}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")