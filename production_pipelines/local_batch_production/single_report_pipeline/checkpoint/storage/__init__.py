#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查点存储模块
提供可插拔的存储后端实现
"""

from .base_storage import CheckpointStorage
from .file_storage import FileCheckpointStorage

__all__ = [
    'CheckpointStorage',
    'FileCheckpointStorage'
]