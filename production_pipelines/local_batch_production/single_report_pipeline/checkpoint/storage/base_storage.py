#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查点存储抽象基类
定义存储接口契约，支持多种存储后端
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models.checkpoint_data import CheckpointData


class CheckpointStorage(ABC):
    """
    检查点存储抽象基类

    定义了检查点存储的核心接口，支持不同的存储后端实现
    """

    @abstractmethod
    def save(self, checkpoint: CheckpointData) -> bool:
        """
        保存检查点数据

        Args:
            checkpoint: 要保存的检查点数据

        Returns:
            保存是否成功
        """
        pass

    @abstractmethod
    def load(self) -> Optional[CheckpointData]:
        """
        加载检查点数据

        Returns:
            加载的检查点数据，如果不存在或加载失败返回None
        """
        pass

    @abstractmethod
    def exists(self) -> bool:
        """
        检查检查点是否存在

        Returns:
            检查点是否存在
        """
        pass

    @abstractmethod
    def delete(self) -> bool:
        """
        删除检查点

        Returns:
            删除是否成功
        """
        pass

    def is_valid_checkpoint(self, checkpoint: CheckpointData) -> bool:
        """
        验证检查点数据的有效性

        Args:
            checkpoint: 要验证的检查点数据

        Returns:
            数据是否有效
        """
        if checkpoint is None:
            return False

        return checkpoint.is_valid()

    def get_storage_info(self) -> dict:
        """
        获取存储信息

        Returns:
            存储信息字典
        """
        return {
            "storage_type": self.__class__.__name__,
            "initialized": True
        }