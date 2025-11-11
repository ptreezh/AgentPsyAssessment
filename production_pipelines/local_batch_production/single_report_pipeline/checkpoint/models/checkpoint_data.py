#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查点数据模型
包含完整的检查点信息，用于数据持久化
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field

from .processing_state import ProcessingState


@dataclass
class CheckpointData:
    """
    检查点数据类

    包含完整的处理状态和元数据，支持版本兼容性
    """
    # 基本信息
    version: str = "2.0"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    checkpoint_id: str = field(default_factory=lambda: f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # 处理状态
    processing_state: ProcessingState = field(default_factory=ProcessingState)

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        # 确保timestamp是字符串格式
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.isoformat()

    def to_json(self) -> str:
        """
        序列化为JSON字符串

        Returns:
            JSON格式的检查点数据
        """
        data = asdict(self)
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_data: str) -> 'CheckpointData':
        """
        从JSON字符串反序列化

        Args:
            json_data: JSON格式的检查点数据

        Returns:
            CheckpointData实例
        """
        try:
            data = json.loads(json_data)

            if not isinstance(data, dict):
                raise ValueError("Invalid JSON data structure")

            # 处理版本兼容性
            if 'version' not in data:
                data['version'] = "1.0"

            # 提取处理状态
            if 'processing_state' in data:
                processing_state_data = json.dumps(data['processing_state'])
                processing_state = ProcessingState.from_json(processing_state_data)
            else:
                processing_state = ProcessingState()

            # 提取元数据
            metadata = data.get('metadata', {})

            return cls(
                version=data.get('version', '2.0'),
                timestamp=data.get('timestamp', datetime.now().isoformat()),
                checkpoint_id=data.get('checkpoint_id', f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                processing_state=processing_state,
                metadata=metadata
            )

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ValueError(f"无法解析检查点数据: {e}")

    def is_valid(self) -> bool:
        """
        验证检查点数据的有效性

        Returns:
            数据是否有效
        """
        # 检查基本字段
        if not self.version:
            return False

        if not self.checkpoint_id:
            return False

        # 检查处理状态
        if not self.processing_state.is_valid():
            return False

        return True

    def update_metadata(self, **kwargs):
        """
        更新元数据

        Args:
            **kwargs: 元数据字段
        """
        self.metadata.update(kwargs)
        self.metadata["last_updated"] = datetime.now().isoformat()

    def get_progress_summary(self) -> Dict[str, Any]:
        """
        获取进度摘要

        Returns:
            进度摘要信息
        """
        return {
            "checkpoint_id": self.checkpoint_id,
            "timestamp": self.timestamp,
            "version": self.version,
            "current_file": self.processing_state.current_file_path,
            "current_question": self.processing_state.current_question_index,
            "progress_percentage": self.processing_state.get_progress_percentage(),
            "processed_files": len(self.processing_state.processed_files),
            "total_files": self.processing_state.total_files
        }

    def __str__(self) -> str:
        """字符串表示"""
        progress = self.processing_state.get_progress_percentage()
        return (
            f"CheckpointData("
            f"id={self.checkpoint_id}, "
            f"progress={progress:.1f}%, "
            f"file={self.processing_state.current_file_path})"
        )

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()