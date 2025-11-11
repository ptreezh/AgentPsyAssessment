#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件存储实现
基于文件系统的检查点存储，支持备份和恢复
"""

import json
import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .base_storage import CheckpointStorage
from ..models.checkpoint_data import CheckpointData


class FileCheckpointStorage(CheckpointStorage):
    """
    基于文件系统的检查点存储实现

    提供可靠、高性能的文件存储，支持自动备份和并发安全
    """

    def __init__(self, storage_dir: str, filename: str = "checkpoint.json", max_backups: int = 5):
        """
        初始化文件存储

        Args:
            storage_dir: 存储目录路径
            filename: 检查点文件名
            max_backups: 最大备份数量
        """
        self.storage_dir = Path(storage_dir)
        self.filename = filename
        self.max_backups = max_backups

        # 确保目录存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        self.checkpoint_file = self.storage_dir / filename
        self.backup_dir = self.storage_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # 并发控制
        self._lock = threading.Lock()

        # 验证存储目录可写
        self._validate_storage_directory()

    def _validate_storage_directory(self):
        """验证存储目录是否可写"""
        if not os.access(self.storage_dir, os.W_OK):
            raise PermissionError(f"存储目录不可写: {self.storage_dir}")

        # 尝试创建测试文件
        test_file = self.storage_dir / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            raise PermissionError(f"存储目录写入测试失败: {e}")

    def save(self, checkpoint: CheckpointData) -> bool:
        """
        保存检查点到文件

        Args:
            checkpoint: 要保存的检查点数据

        Returns:
            保存是否成功
        """
        if not self.is_valid_checkpoint(checkpoint):
            return False

        with self._lock:
            try:
                # 创建备份
                self._create_backup()

                # 原子写入：先写入临时文件，然后重命名
                temp_file = self.checkpoint_file.with_suffix('.tmp')
                json_data = checkpoint.to_json()

                temp_file.write_text(json_data, encoding='utf-8')

                # 原子重命名
                temp_file.replace(self.checkpoint_file)

                # 清理旧备份
                self._cleanup_old_backups()

                return True

            except Exception as e:
                # 记录错误但不抛出异常
                print(f"保存检查点失败: {e}")
                return False

    def load(self) -> Optional[CheckpointData]:
        """
        从文件加载检查点

        Returns:
            加载的检查点数据，如果不存在或加载失败返回None
        """
        if not self.exists():
            return None

        with self._lock:
            try:
                # 尝试加载主文件
                checkpoint = self._load_from_file(self.checkpoint_file)
                if checkpoint:
                    return checkpoint

                # 如果主文件损坏，尝试从备份恢复
                return self._recover_from_backup()

            except Exception as e:
                print(f"加载检查点失败: {e}")
                return None

    def exists(self) -> bool:
        """
        检查检查点文件是否存在且有效

        Returns:
            检查点是否存在
        """
        if not self.checkpoint_file.exists():
            return False

        try:
            # 尝试解析文件内容
            checkpoint = self._load_from_file(self.checkpoint_file)
            return checkpoint is not None

        except Exception:
            return False

    def delete(self) -> bool:
        """
        删除检查点文件

        Returns:
            删除是否成功
        """
        with self._lock:
            try:
                if self.checkpoint_file.exists():
                    self.checkpoint_file.unlink()
                return True

            except Exception as e:
                print(f"删除检查点失败: {e}")
                return False

    def _load_from_file(self, file_path: Path) -> Optional[CheckpointData]:
        """从指定文件加载检查点"""
        try:
            if not file_path.exists():
                return None

            json_data = file_path.read_text(encoding='utf-8')
            checkpoint = CheckpointData.from_json(json_data)
            return checkpoint

        except Exception:
            return None

    def _create_backup(self):
        """创建备份文件"""
        if not self.checkpoint_file.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"checkpoint_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename

        try:
            shutil.copy2(self.checkpoint_file, backup_path)
        except Exception as e:
            print(f"创建备份失败: {e}")

    def _cleanup_old_backups(self):
        """清理旧备份文件，保留最新的max_backups个"""
        try:
            backup_files = list(self.backup_dir.glob("checkpoint_backup_*.json"))
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # 删除超出数量限制的旧备份
            for backup_file in backup_files[self.max_backups:]:
                backup_file.unlink()

        except Exception as e:
            print(f"清理备份文件失败: {e}")

    def _recover_from_backup(self) -> Optional[CheckpointData]:
        """从备份文件恢复"""
        try:
            backup_files = list(self.backup_dir.glob("checkpoint_backup_*.json"))
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            for backup_file in backup_files:
                checkpoint = self._load_from_file(backup_file)
                if checkpoint:
                    # 恢复成功，复制到主文件
                    shutil.copy2(backup_file, self.checkpoint_file)
                    print(f"从备份恢复检查点: {backup_file.name}")
                    return checkpoint

            return None

        except Exception as e:
            print(f"从备份恢复失败: {e}")
            return None

    def get_backup_count(self) -> int:
        """获取备份文件数量"""
        try:
            return len(list(self.backup_dir.glob("checkpoint_backup_*.json")))
        except Exception:
            return 0

    def get_file_size(self) -> int:
        """获取检查点文件大小（字节）"""
        try:
            return self.checkpoint_file.stat().st_size if self.checkpoint_file.exists() else 0
        except Exception:
            return 0

    def get_storage_info(self) -> dict:
        """
        获取文件存储的详细信息

        Returns:
            存储信息字典
        """
        info = super().get_storage_info()
        info.update({
            "storage_type": self.__class__.__name__,
            "storage_dir": str(self.storage_dir),
            "checkpoint_file": str(self.checkpoint_file),
            "file_exists": self.checkpoint_file.exists(),
            "file_size": self.get_file_size(),
            "backup_count": self.get_backup_count(),
            "max_backups": self.max_backups
        })
        return info

    def __str__(self) -> str:
        """字符串表示"""
        return f"FileCheckpointStorage(dir={self.storage_dir}, file={self.filename})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()