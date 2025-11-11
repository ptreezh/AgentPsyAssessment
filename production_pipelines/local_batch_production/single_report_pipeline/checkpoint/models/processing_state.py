#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理状态数据模型
跟踪批量处理的详细进度信息
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class ProcessingState:
    """
    批量处理状态数据类

    跟踪文件级别和题目级别的处理进度，支持精确的断点续跑
    """
    # 基本信息
    version: str = "2.0"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 当前处理位置
    current_file_path: str = ""
    current_question_index: int = 0
    current_file_index: int = 0
    total_files: int = 0

    # 已完成文件列表
    processed_files: List[str] = field(default_factory=list)

    # 文件进度详情
    file_progress: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 统计信息
    statistics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        # 确保timestamp是字符串格式
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.isoformat()

    def to_json(self) -> str:
        """
        序列化为JSON字符串

        Returns:
            JSON格式的状态数据
        """
        data = asdict(self)
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_data: str) -> 'ProcessingState':
        """
        从JSON字符串反序列化

        Args:
            json_data: JSON格式的状态数据

        Returns:
            ProcessingState实例
        """
        try:
            data = json.loads(json_data)

            # 处理版本兼容性
            if isinstance(data, dict):
                # 确保必需字段存在
                if 'version' not in data:
                    data['version'] = "1.0"  # 旧版本

                if 'statistics' not in data:
                    data['statistics'] = {}

                if 'file_progress' not in data:
                    data['file_progress'] = {}

                if 'processed_files' not in data:
                    data['processed_files'] = []

                # 处理旧版本字段
                if 'total_questions' in data and 'total_files' not in data:
                    # 旧版本只有总题目数，估算文件数
                    data['total_files'] = (data['total_questions'] + 49) // 50

                return cls(**data)
            else:
                raise ValueError("Invalid JSON data structure")

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ValueError(f"无法解析处理状态数据: {e}")

    def is_valid(self) -> bool:
        """
        验证状态数据的有效性

        Returns:
            数据是否有效
        """
        # 检查基本字段
        if self.current_question_index < 0:
            return False

        if self.current_file_index < 0:
            return False

        if self.total_files < 0:
            return False

        if self.current_file_index >= self.total_files and self.total_files > 0:
            return False

        # 检查路径格式
        if self.current_file_path and not isinstance(self.current_file_path, str):
            return False

        return True

    def update_progress(self, file_path: str, question_index: int, file_index: int = None):
        """
        更新处理进度

        Args:
            file_path: 当前处理文件路径
            question_index: 当前题目索引
            file_index: 当前文件索引（可选）
        """
        self.current_file_path = file_path
        self.current_question_index = question_index
        self.timestamp = datetime.now().isoformat()

        if file_index is not None:
            self.current_file_index = file_index

    def mark_file_completed(self, file_path: str, total_questions: int):
        """
        标记文件处理完成

        Args:
            file_path: 文件路径
            total_questions: 文件总题目数
        """
        if file_path not in self.processed_files:
            self.processed_files.append(file_path)

        # 更新文件进度
        self.file_progress[file_path] = {
            "total_questions": total_questions,
            "processed_questions": total_questions,
            "completed_at": datetime.now().isoformat()
        }

    def update_file_progress(self, file_path: str, processed_questions: int, total_questions: int):
        """
        更新文件处理进度

        Args:
            file_path: 文件路径
            processed_questions: 已处理题目数
            total_questions: 总题目数
        """
        self.file_progress[file_path] = {
            "total_questions": total_questions,
            "processed_questions": processed_questions,
            "updated_at": datetime.now().isoformat()
        }

    def get_resume_point(self) -> Optional[tuple]:
        """
        获取续跑点

        Returns:
            (文件路径, 题目索引) 或 None
        """
        if self.current_file_path and self.current_question_index >= 0:
            return (self.current_file_path, self.current_question_index)
        return None

    def get_total_processed_questions(self) -> int:
        """
        获取已处理题目总数

        Returns:
            已处理题目总数
        """
        total = 0

        # 已完成文件的题目数
        for file_path in self.processed_files:
            if file_path in self.file_progress:
                total += self.file_progress[file_path].get("processed_questions", 0)
            else:
                # 如果没有进度信息，假设每个文件50题
                total += 50

        # 当前文件已处理题目数（如果当前文件不在已完成列表中）
        if self.current_file_path and self.current_file_path not in self.processed_files:
            total += self.current_question_index

        return total

    def get_total_questions(self) -> int:
        """
        获取总题目数

        Returns:
            总题目数
        """
        if self.total_files > 0:
            # 假设每个文件50题（根据实际情况调整）
            return self.total_files * 50
        return 0

    def get_progress_percentage(self) -> float:
        """
        获取处理进度百分比

        Returns:
            进度百分比 (0-100)
        """
        total_questions = self.get_total_questions()
        if total_questions == 0:
            return 0.0

        processed = self.get_total_processed_questions()
        return (processed / total_questions) * 100

    def update_statistics(self, **kwargs):
        """
        更新统计信息

        Args:
            **kwargs: 统计字段
        """
        self.statistics.update(kwargs)
        self.statistics["last_updated"] = datetime.now().isoformat()

    def is_file_completed(self, file_path: str) -> bool:
        """
        检查文件是否已完成

        Args:
            file_path: 文件路径

        Returns:
            文件是否已完成
        """
        return file_path in self.processed_files

    def get_file_progress(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件处理进度

        Args:
            file_path: 文件路径

        Returns:
            进度信息字典
        """
        return self.file_progress.get(file_path, {
            "total_questions": 0,
            "processed_questions": 0
        })

    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, ProcessingState):
            return False

        return (
            self.current_file_path == other.current_file_path and
            self.current_question_index == other.current_question_index and
            self.current_file_index == other.current_file_index and
            self.total_files == other.total_files and
            self.processed_files == other.processed_files
        )

    def __str__(self) -> str:
        """字符串表示"""
        progress = self.get_progress_percentage()
        return (
            f"ProcessingState("
            f"file={self.current_file_path}, "
            f"question={self.current_question_index}, "
            f"progress={progress:.1f}%)"
        )

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()