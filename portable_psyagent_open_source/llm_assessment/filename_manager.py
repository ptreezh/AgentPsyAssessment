#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件名管理工具 - 处理文件名冲突和唯一性问题
"""

import os
from typing import Dict, List

class FilenameManager:
    """文件名管理器"""
    
    @staticmethod
    def get_unique_filename(base_path: str, base_name: str, extension: str = "") -> str:
        """
        获取唯一的文件名，如果文件已存在则添加序号
        
        Args:
            base_path: 基础路径
            base_name: 基础文件名
            extension: 文件扩展名（包括点号，如 ".json"）
            
        Returns:
            唯一的文件路径
        """
        # 确保扩展名以点号开头
        if extension and not extension.startswith("."):
            extension = "." + extension
            
        full_name = base_name + extension
        full_path = os.path.join(base_path, full_name)
        
        # 如果文件不存在，直接返回
        if not os.path.exists(full_path):
            return full_path
            
        # 文件已存在，添加序号
        counter = 1
        while True:
            numbered_name = f"{base_name}_{counter}{extension}"
            numbered_path = os.path.join(base_path, numbered_name)
            if not os.path.exists(numbered_path):
                return numbered_path
            counter += 1
    
    @staticmethod
    def ensure_unique_task_name(task_name: str, existing_names: List[str]) -> str:
        """
        确保任务名称唯一
        
        Args:
            task_name: 原始任务名称
            existing_names: 已存在的任务名称列表
            
        Returns:
            唯一的任务名称
        """
        if task_name not in existing_names:
            return task_name
            
        # 任务名称已存在，添加序号
        counter = 1
        while True:
            numbered_name = f"{task_name}_{counter}"
            if numbered_name not in existing_names:
                return numbered_name
            counter += 1

# 使用示例
if __name__ == "__main__":
    # 示例：处理文件名冲突
    manager = FilenameManager()
    
    # 创建测试目录
    test_dir = "test_output"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 创建一个测试文件
    test_file = os.path.join(test_dir, "test_result.json")
    with open(test_file, "w") as f:
        f.write("{}")
    
    # 获取唯一的文件名
    unique_file = manager.get_unique_filename(test_dir, "test_result", ".json")
    print(f"唯一文件名: {unique_file}")
    
    # 清理测试文件
    os.remove(test_file)
    os.rmdir(test_dir)