#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度跟踪器
细粒度进度跟踪和检查点管理的高级API
"""

import time
import threading
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from .checkpoint_manager import CheckpointManager
from .models.checkpoint_data import CheckpointData
from .models.processing_state import ProcessingState
from .storage.base_storage import CheckpointStorage


class ProgressTracker:
    """
    进度跟踪器

    提供高级API来跟踪批量处理进度，支持细粒度检查点和自动恢复
    """

    def __init__(self, storage: CheckpointStorage, checkpoint_interval: int = 5,
                 auto_save: bool = True, session_metadata: Optional[Dict[str, Any]] = None):
        """
        初始化进度跟踪器

        Args:
            storage: 存储后端实例
            checkpoint_interval: 检查点间隔（题目数）
            auto_save: 是否启用自动保存
            session_metadata: 会话元数据
        """
        self.storage = storage
        self.checkpoint_interval = checkpoint_interval
        self.auto_save_enabled = auto_save
        self.session_metadata = session_metadata or {}

        # 创建检查点管理器
        self.checkpoint_manager = CheckpointManager(storage, auto_save=auto_save)

        # 当前处理状态
        self.current_state: Optional[ProcessingState] = None
        self.session_id: Optional[str] = None
        self.session_start_time: Optional[float] = None

        # 进度跟踪
        self.last_checkpoint_question_count = 0
        self.total_questions_in_current_file = 0

        # 并发控制
        self._lock = threading.Lock()

    def start_new_session(self, file_list: List[str]) -> str:
        """
        开始新的处理会话

        Args:
            file_list: 要处理的文件列表

        Returns:
            会话ID
        """
        with self._lock:
            # 生成会话ID
            self.session_id = str(uuid.uuid4())
            self.session_start_time = time.time()

            # 初始化处理状态
            self.current_state = ProcessingState(
                current_file_path="",
                current_question_index=0,
                total_files=len(file_list),
                processed_files=[],
                file_progress={},
                statistics={}
            )

            # 创建初始检查点
            checkpoint = CheckpointData(
                checkpoint_id=self.session_id,
                processing_state=self.current_state,
                metadata={
                    **self.session_metadata,
                    "session_start": True,
                    "total_files": len(file_list),
                    "file_list": file_list
                }
            )

            self.checkpoint_manager.save_checkpoint(checkpoint)
            self.last_checkpoint_question_count = 0

            return self.session_id

    def checkpoint_exists(self) -> bool:
        """
        检查是否存在检查点

        Returns:
            是否存在检查点
        """
        return self.storage.exists()

    def resume_from_checkpoint(self) -> bool:
        """
        从检查点恢复会话

        Returns:
            是否成功恢复
        """
        with self._lock:
            # 尝试加载检查点
            checkpoint = self.checkpoint_manager.load_checkpoint()
            if checkpoint is None:
                return False

            # 恢复状态
            self.current_state = checkpoint.processing_state
            self.session_id = checkpoint.checkpoint_id

            # 更新进度跟踪变量
            if self.current_state.current_file_path:
                file_progress = self.current_state.file_progress.get(self.current_state.current_file_path, {})
                self.total_questions_in_current_file = file_progress.get("total_questions", 0)
                self.last_checkpoint_question_count = self.current_state.current_question_index

            return True

    def update_file_progress(self, file_path: str, current_question: int,
                           total_questions: Optional[int] = None) -> bool:
        """
        更新文件处理进度

        Args:
            file_path: 文件路径
            current_question: 当前题目索引
            total_questions: 文件总题目数（可选）

        Returns:
            是否成功更新
        """
        if self.current_state is None or self.session_id is None:
            return False

        with self._lock:
            # 更新当前状态
            self.current_state.current_file_path = file_path
            self.current_state.current_question_index = current_question

            # 更新文件进度信息
            if file_path not in self.current_state.file_progress:
                self.current_state.file_progress[file_path] = {
                    "total_questions": total_questions or 50,
                    "processed_questions": 0,
                    "start_time": time.time()
                }

            # 更新进度
            file_progress = self.current_state.file_progress[file_path]
            if total_questions:
                file_progress["total_questions"] = total_questions
            file_progress["processed_questions"] = max(file_progress["processed_questions"], current_question)

            # 检查是否需要保存检查点
            should_save = (current_question - self.last_checkpoint_question_count) >= self.checkpoint_interval

            if should_save and self.auto_save_enabled:
                self._save_checkpoint({
                    "auto_save": True,
                    "checkpoint_reason": "interval_reached",
                    "questions_processed": current_question
                })
                self.last_checkpoint_question_count = current_question

            return True

    def mark_file_completed(self, file_path: str, file_statistics: Optional[Dict[str, Any]] = None) -> bool:
        """
        标记文件处理完成

        Args:
            file_path: 文件路径
            file_statistics: 文件统计信息

        Returns:
            是否成功标记
        """
        if self.current_state is None or self.session_id is None:
            return False

        with self._lock:
            # 添加到已完成列表
            if file_path not in self.current_state.processed_files:
                self.current_state.processed_files.append(file_path)

            # 更新文件进度
            if file_path in self.current_state.file_progress:
                file_progress = self.current_state.file_progress[file_path]
                file_progress["completed"] = True
                file_progress["completion_time"] = time.time()

            # 更新统计信息
            if file_statistics:
                for key, value in file_statistics.items():
                    if key in self.current_state.statistics:
                        self.current_state.statistics[key] += value
                    else:
                        self.current_state.statistics[key] = value

            # 重置当前文件状态
            self.current_state.current_file_path = None
            self.current_state.current_question_index = 0
            self.last_checkpoint_question_count = 0

            # 保存检查点
            if self.auto_save_enabled:
                self._save_checkpoint({
                    "auto_save": True,
                    "checkpoint_reason": "file_completed",
                    "completed_file": file_path
                })

            return True

    def get_resume_point(self) -> Optional[Tuple[str, int, int]]:
        """
        获取恢复点信息

        Returns:
            (文件路径, 题目索引, 已完成文件数) 或 None
        """
        if self.current_state is None:
            return None

        return (
            self.current_state.current_file_path,
            self.current_state.current_question_index,
            len(self.current_state.processed_files)
        )

    def get_progress_summary(self) -> Dict[str, Any]:
        """
        获取进度摘要

        Returns:
            进度摘要字典
        """
        if self.current_state is None:
            return {
                "total_files": 0,
                "processed_files": 0,
                "current_file": None,
                "current_question": 0,
                "progress_percentage": 0.0,
                "statistics": {},
                "session_id": None
            }

        # 计算进度百分比
        total_completed = len(self.current_state.processed_files)
        if self.current_state.current_file_path and self.current_state.current_question_index > 0:
            # 当前文件部分完成
            progress_percentage = (total_completed / self.current_state.total_files) * 100
        else:
            # 基于已完成文件数计算
            progress_percentage = (total_completed / self.current_state.total_files) * 100 if self.current_state.total_files > 0 else 0.0

        return {
            "total_files": self.current_state.total_files,
            "processed_files": total_completed,
            "current_file": self.current_state.current_file_path,
            "current_question": self.current_state.current_question_index,
            "progress_percentage": progress_percentage,
            "statistics": self.current_state.statistics.copy(),
            "session_id": self.session_id,
            "is_completed": False  # 默认值，实际状态通过元数据判断
        }

    def mark_session_completed(self) -> Optional[float]:
        """
        标记会话完成

        Returns:
            完成时间戳
        """
        if self.current_state is None or self.session_id is None:
            return None

        with self._lock:
            completion_time = time.time()

            # 保存最终检查点
            self._save_checkpoint({
                "session_completed": True,
                "completion_time": completion_time,
                "total_session_time": completion_time - (self.session_start_time or completion_time)
            })

            return completion_time

    def set_auto_save(self, enabled: bool):
        """
        设置自动保存

        Args:
            enabled: 是否启用自动保存
        """
        self.auto_save_enabled = enabled
        self.checkpoint_manager.set_auto_save(enabled)

    def set_checkpoint_interval(self, interval: int):
        """
        设置检查点间隔

        Args:
            interval: 检查点间隔（题目数）
        """
        if interval > 0:
            self.checkpoint_interval = interval

    def force_save_checkpoint(self, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        强制保存检查点

        Args:
            metadata: 额外的元数据

        Returns:
            是否成功保存
        """
        if self.current_state is None or self.session_id is None:
            return False

        checkpoint_metadata = {"manual_save": True}
        if metadata:
            checkpoint_metadata.update(metadata)

        return self._save_checkpoint(checkpoint_metadata)

    def _save_checkpoint(self, additional_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存检查点（内部方法）

        Args:
            additional_metadata: 额外的元数据

        Returns:
            是否成功保存
        """
        if self.current_state is None or self.session_id is None:
            return False

        # 构建元数据
        metadata = {
            **self.session_metadata,
            "checkpoint_time": time.time(),
            "session_id": self.session_id
        }

        if additional_metadata:
            metadata.update(additional_metadata)

        # 创建检查点
        checkpoint = CheckpointData(
            checkpoint_id=self.session_id,
            processing_state=self.current_state,
            metadata=metadata
        )

        # 保存检查点
        return self.checkpoint_manager.save_checkpoint(checkpoint)

    def __str__(self) -> str:
        """字符串表示"""
        return f"ProgressTracker(session={self.session_id}, interval={self.checkpoint_interval})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()