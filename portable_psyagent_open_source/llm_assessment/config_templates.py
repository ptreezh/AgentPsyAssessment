#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置模板系统 - 解决批量评估参数配置复杂性问题
提供预设模板和智能参数组合功能
"""

import json
import itertools
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from .filename_manager import FilenameManager

class TestType(Enum):
    BASELINE = "baseline"
    STRESS_TEST = "stress_test"
    CONTEXT_TEST = "context_test"
    FULL_MATRIX = "full_matrix"
    CUSTOM = "custom"

class ParameterMode(Enum):
    SINGLE = "single"
    RANGE = "range"
    SMART_SAMPLE = "smart_sample"
    FULL_COMBINATION = "full_combination"

@dataclass
class TestConfig:
    """测试配置数据结构"""
    name: str
    test_type: TestType
    models: List[str]
    test_files: List[str]
    roles: List[str]
    parameters: Dict[str, Any]
    description: str = ""
    estimated_tasks: int = 0

class ConfigTemplateManager:
    """配置模板管理器"""
    
    def __init__(self):
        self.templates = self._load_default_templates()
        self.generated_task_names = set()  # 跟踪已生成的任务名称
    
    def _load_default_templates(self) -> Dict[str, Dict]:
        """加载默认配置模板"""
        return {
            "baseline": {
                "name": "基线评估",
                "description": "无干扰条件下的基础性能评估",
                "parameters": {
                    "emotional_stress_level": [0],
                    "cognitive_trap_type": [None],
                    "temperature": [0.7],
                    "context_length_mode": ["none"]
                },
                "estimated_multiplier": 1
            },
            "stress_test": {
                "name": "压力评估",
                "description": "情绪压力和认知陷阱评估",
                "parameters": {
                    "emotional_stress_level": [0, 1, 2, 3],
                    "cognitive_trap_type": [None, "p", "c", "s"],
                    "temperature": [0.3, 0.7, 1.3],
                    "context_length_mode": ["none"]
                },
                "estimated_multiplier": 36  # 4 * 4 * 3
            },
            "context_test": {
                "name": "上下文评估",
                "description": "不同上下文长度对性能的影响",
                "parameters": {
                    "emotional_stress_level": [0],
                    "cognitive_trap_type": [None],
                    "temperature": [0.7],
                    "context_length_mode": ["auto", "static", "dynamic"],
                    "static_context_length": [1, 4, 16, 32],
                    "dynamic_context_ratio": ["1/4", "1/2", "3/4"]
                },
                "estimated_multiplier": 12  # 3 * 4 * 3 (条件依赖)
            },
            "full_matrix": {
                "name": "全矩阵评估",
                "description": "所有参数组合的完整评估",
                "parameters": {
                    "emotional_stress_level": [0, 1, 2, 3, 4],
                    "cognitive_trap_type": [None, "p", "c", "s", "r"],
                    "temperature": [0.0, 0.3, 0.7, 1.0, 1.3, 1.8],
                    "context_length_mode": ["none", "auto", "static", "dynamic"],
                    "static_context_length": [0, 1, 4, 8, 16, 32],
                    "dynamic_context_ratio": ["1/4", "1/3", "1/2", "2/3", "3/4"]
                },
                "estimated_multiplier": 900,  # 警告：会产生大量任务
                "warning": "此模板会产生大量任务，请谨慎使用"
            },
            "quick_validation": {
                "name": "快速验证",
                "description": "快速验证模型基本功能",
                "parameters": {
                    "emotional_stress_level": [0, 2],
                    "cognitive_trap_type": [None, "p"],
                    "temperature": [0.7],
                    "context_length_mode": ["none", "auto"]
                },
                "estimated_multiplier": 8
            },
            "temperature_sweep": {
                "name": "温度扫描",
                "description": "评估不同温度参数对结果的影响",
                "parameters": {
                    "emotional_stress_level": [0],
                    "cognitive_trap_type": [None],
                    "temperature": [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.2, 1.5, 1.8, 2.0],
                    "context_length_mode": ["none"]
                },
                "estimated_multiplier": 11
            }
        }
    
    def get_template(self, template_name: str) -> Optional[Dict]:
        """获取指定模板"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[Dict]:
        """列出所有可用模板"""
        return [
            {
                "name": name,
                "display_name": config["name"],
                "description": config["description"],
                "estimated_multiplier": config["estimated_multiplier"],
                "warning": config.get("warning", "")
            }
            for name, config in self.templates.items()
        ]
    
    def calculate_task_count(self, template_name: str, models: List[str], 
                           test_files: List[str], roles: List[str]) -> int:
        """计算预计任务数量"""
        template = self.get_template(template_name)
        if not template:
            return 0
        
        param_combinations = 1
        for param_values in template["parameters"].values():
            param_combinations *= len(param_values)
        
        return len(models) * len(test_files) * len(roles) * param_combinations
    
    def generate_config(self, template_name: str, models: List[str], 
                       test_files: List[str], roles: List[str], 
                       custom_params: Optional[Dict] = None) -> Dict:
        """基于模板生成配置"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # 使用自定义参数或模板参数
        parameters = custom_params or template["parameters"]
        
        # 生成所有参数组合
        param_names = list(parameters.keys())
        param_values = list(parameters.values())
        
        tasks = []
        task_id = 1
        
        # 生成参数组合的笛卡尔积
        for combination in itertools.product(*param_values):
            param_dict = dict(zip(param_names, combination))
            
            # 跳过无效组合（如context_mode=none时忽略context_length）
            if self._is_valid_combination(param_dict):
                for model in models:
                    for test_file in test_files:
                        for role in roles:
                            task = self._create_task(task_id, model, test_file, role, param_dict)
                            tasks.append(task)
                            task_id += 1
        
        # 构建配置
        config_models = [{"name": m.replace("/", "_").replace(":", "-"), "path": m} 
                        for m in models]
        
        return {
            "models": config_models,
            "test_suites": [{
                "suite_name": f"{template_name}_{len(models)}models_{len(tasks)}tasks",
                "models_to_run": [m["name"] for m in config_models],
                "tasks": tasks
            }],
            "metadata": {
                "template_used": template_name,
                "total_tasks": len(tasks),
                "models_count": len(models),
                "test_files_count": len(test_files),
                "roles_count": len(roles),
                "generated_at": "2024-01-01T00:00:00Z"
            }
        }
    
    def _is_valid_combination(self, params: Dict) -> bool:
        """检查参数组合是否有效"""
        # 上下文模式相关的验证
        if params.get("context_length_mode") == "none":
            # 如果context_mode为none，忽略context_length相关参数
            params.pop("static_context_length", None)
            params.pop("dynamic_context_ratio", None)
        
        if params.get("context_length_mode") == "static":
            # static模式需要static_context_length
            return "static_context_length" in params
        
        if params.get("context_length_mode") == "dynamic":
            # dynamic模式需要dynamic_context_ratio
            return "dynamic_context_ratio" in params
        
        return True
    
    def _create_task(self, task_id: int, model: str, test_file: str, 
                    role: str, params: Dict) -> Dict:
        """创建单个任务配置"""
        task_name_parts = [
            f"task{task_id:03d}",
            model.split("/")[-1].replace(":", "-").replace(".", "_"),
            test_file.replace(".json", "").replace(".", "_").replace("/", "_").replace("\\", "_"),
            role.replace(".txt", "").replace(".", "_").replace("/", "_").replace("\\", "_")
        ]
        
        # 添加参数标识（按排序顺序确保一致性）
        param_parts = []
        # 对参数进行排序以确保一致性
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        for key, value in sorted_params:
            if value is not None and key != "context_length_mode":
                # 使用更完整的参数映射
                short_key = {
                    "emotional_stress_level": "es",
                    "cognitive_trap_type": "ct",
                    "temperature": "tmp",
                    "static_context_length": "cl",
                    "dynamic_context_ratio": "cr"
                }.get(key, key[:2])  # 使用前两个字符作为默认短键
                
                # 处理特殊值
                if isinstance(value, (int, float)):
                    # 对数值进行格式化，避免小数点问题
                    value_str = f"{value:g}".replace(".", "p")  # 用p代替小数点
                else:
                    # 对字符串值进行清理
                    value_str = str(value).replace(".", "_").replace("/", "_").replace("\\", "_")
                
                param_parts.append(f"{short_key}{value_str}")
        
        if param_parts:
            task_name_parts.extend(param_parts)
        
        # 清理特殊字符以确保文件名兼容性
        cleaned_parts = []
        for part in task_name_parts:
            # 移除或替换不安全的字符
            cleaned_part = str(part)
            for char in ['<', '>', ':', '"', '|', '?', '*', ' ', '	']:
                cleaned_part = cleaned_part.replace(char, '_')
            # 限制长度以避免过长的文件名
            if len(cleaned_part) > 30:
                cleaned_part = cleaned_part[:30]
            cleaned_parts.append(cleaned_part)
        
        base_task_name = "_".join(cleaned_parts)
        
        task = {
            "task_name": base_task_name,
            "type": "questionnaire",
            "test_file": test_file,
        }
        
        # 添加非默认参数
        for key, value in params.items():
            if value is not None:
                task[key] = value
        
        if role != "default":
            task["role_file"] = role
        
        return task
    
    def create_smart_config(self, models: List[str], test_files: List[str], 
                          roles: List[str], max_tasks: int = 100) -> Dict:
        """创建智能配置，避免任务过多"""
        # 计算每个模板的任务数
        template_scores = []
        for name, template in self.templates.items():
            task_count = self.calculate_task_count(name, models, test_files, roles)
            if task_count <= max_tasks:
                template_scores.append((name, task_count, template["description"]))
        
        if not template_scores:
            # 如果没有合适的模板，创建自定义配置
            return self._create_limited_config(models, test_files, roles, max_tasks)
        
        # 选择最接近max_tasks的模板
        best_template = max(template_scores, key=lambda x: x[1])
        return self.generate_config(best_template[0], models, test_files, roles)
    
    def _create_limited_config(self, models: List[str], test_files: List[str], 
                             roles: List[str], max_tasks: int) -> Dict:
        """创建限制任务数量的配置"""
        # 智能采样参数
        limited_params = {
            "emotional_stress_level": [0, 2, 4],
            "cognitive_trap_type": [None, "p", "s"],
            "temperature": [0.3, 0.7, 1.3],
            "context_length_mode": ["none", "auto"]
        }
        
        return self.generate_config("custom", models, test_files, roles, limited_params)
    
    def _generate_unique_filename(self, base_name: str, extension: str = "", 
                                 target_directory: str = ".") -> str:
        """
        生成唯一的文件名，如果文件已存在则添加序号
        
        Args:
            base_name: 基础文件名
            extension: 文件扩展名（包括点号，如 ".json"）
            target_directory: 目标目录路径
            
        Returns:
            唯一的文件名
        """
        # 清理文件名中的非法字符
        cleaned_name = base_name
        for char in ['<', '>', ':', '"', '|', '?', '*', '/', '\\']:
            cleaned_name = cleaned_name.replace(char, '_')
        
        # 确保文件名不以点或空格结尾
        cleaned_name = cleaned_name.rstrip('. ')
        
        full_name = cleaned_name + extension
        counter = 1
        unique_name = full_name
        
        # 检查文件是否已存在，如果存在则添加序号
        while os.path.exists(os.path.join(target_directory, unique_name)):
            unique_name = f"{cleaned_name}_{counter}{extension}"
            counter += 1
            # 防止无限循环
            if counter > 1000:
                break
                
        return unique_name

# 使用示例
if __name__ == "__main__":
    manager = ConfigTemplateManager()
    
    # 列出所有模板
    print("可用配置模板:")
    for template in manager.list_templates():
        print(f"- {template['display_name']}: {template['description']}")
        print(f"  预计任务数: {template['estimated_multiplier']} × (模型数 × 测试文件数 × 角色数)")
        if template.get("warning"):
            print(f"  ⚠️  {template['warning']}")
        print()
    
    # 示例：生成baseline配置
    models = ["gemma3:latest", "llama3.2:latest"]
    test_files = ["agent-big-five-50-complete2.json"]
    roles = ["a1.txt", "b1.txt"]
    
    config = manager.generate_config("baseline", models, test_files, roles)
    print(f"生成配置包含 {len(config['test_suites'][0]['tasks'])} 个任务")
    
    # 保存配置
    with open("generated_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("配置已保存到 generated_config.json")