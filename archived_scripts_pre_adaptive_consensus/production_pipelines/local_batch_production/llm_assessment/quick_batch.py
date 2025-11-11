#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速批处理配置生成器
一键响应用户多样化测评需求
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Optional
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from config_templates import ConfigTemplateManager, TestType

class QuickBatchGenerator:
    """快速批处理生成器"""
    
    def __init__(self):
        self.template_manager = ConfigTemplateManager()
        self.models_dir = os.path.join(os.path.dirname(__file__), "test_files")
        self.roles_dir = os.path.join(os.path.dirname(__file__), "roles")
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        # 从配置文件读取
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return list(config.get("models", {}).keys())
        except:
            return ["gemma3:latest", "llama3.2:latest", "qwen2.5:latest"]
    
    def get_available_test_files(self, language: str = "en") -> List[str]:
        """获取可用测试文件"""
        test_files = []
        if os.path.exists(self.models_dir):
            for f in os.listdir(self.models_dir):
                if f.endswith('.json'):
                    if language == "en" and "_en" in f:
                        test_files.append(f)
                    elif language == "zh" and "_en" not in f:
                        test_files.append(f)
                    elif language == "all":
                        test_files.append(f)
        return test_files or ["agent-big-five-50-complete2.json"]
    
    def get_available_roles(self, language: str = "en") -> List[str]:
        """获取可用角色文件"""
        roles = ["default"]
        if os.path.exists(self.roles_dir):
            for f in os.listdir(self.roles_dir):
                if f.endswith('.txt'):
                    if language == "en" and "_en" in f:
                        roles.append(f)
                    elif language == "zh" and "_en" not in f:
                        roles.append(f)
                    elif language == "all":
                        roles.append(f)
        return roles
    
    def interactive_mode(self):
        """交互式模式"""
        print("🚀 快速批处理配置生成器")
        print("=" * 50)
        
        # 语言选择
        print("\n1. 选择语言:")
        print("   1. 英文 (en)")
        print("   2. 中文 (zh)")
        print("   3. 全部 (all)")
        
        lang_choice = input("请选择 (1-3): ").strip()
        language_map = {"1": "en", "2": "zh", "3": "all"}
        language = language_map.get(lang_choice, "en")
        
        # 模板选择
        print("\n2. 选择配置模板:")
        templates = self.template_manager.list_templates()
        for i, template in enumerate(templates, 1):
            print(f"   {i}. {template['display_name']}")
            print(f"      {template['description']}")
            if template.get('warning'):
                print(f"      ⚠️  {template['warning']}")
            print()
        
        template_choice = input("请选择模板 (1-6): ").strip()
        template_map = {"1": "baseline", "2": "stress_test", "3": "context_test", 
                       "4": "full_matrix", "5": "quick_validation", "6": "temperature_sweep"}
        template_name = template_map.get(template_choice, "baseline")
        
        # 模型选择
        models = self.get_available_models()
        print(f"\n3. 选择模型 ({len(models)} 个可用):")
        for i, model in enumerate(models, 1):
            print(f"   {i}. {model}")
        
        model_input = input("输入模型序号 (用逗号分隔，或按回车选择全部): ").strip()
        if model_input:
            selected_models = [models[int(i)-1] for i in model_input.split(",")]
        else:
            selected_models = models
        
        # 测试文件选择
        test_files = self.get_available_test_files(language)
        print(f"\n4. 选择测试文件 ({len(test_files)} 个可用):")
        for i, test in enumerate(test_files, 1):
            print(f"   {i}. {test}")
        
        test_input = input("输入测试文件序号 (用逗号分隔，或按回车选择第一个): ").strip()
        if test_input:
            selected_tests = [test_files[int(i)-1] for i in test_input.split(",")]
        else:
            selected_tests = [test_files[0]]
        
        # 角色选择
        roles = self.get_available_roles(language)
        print(f"\n5. 选择角色 ({len(roles)} 个可用):")
        for i, role in enumerate(roles, 1):
            print(f"   {i}. {role}")
        
        role_input = input("输入角色序号 (用逗号分隔，或按回车选择default): ").strip()
        if role_input:
            selected_roles = [roles[int(i)-1] for i in role_input.split(",")]
        else:
            selected_roles = ["default"]
        
        # 任务数量预估
        task_count = self.template_manager.calculate_task_count(
            template_name, selected_models, selected_tests, selected_roles
        )
        
        print(f"\n📊 配置预览:")
        print(f"   模板: {template_name}")
        print(f"   模型: {len(selected_models)} 个")
        print(f"   测试: {len(selected_tests)} 个")
        print(f"   角色: {len(selected_roles)} 个")
        print(f"   预计任务数: {task_count}")
        
        if task_count > 100:
            print(f"   ⚠️  任务数量较多，可能需要较长时间")
        
        confirm = input("\n确认生成配置? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
        
        # 生成配置
        config = self.template_manager.generate_config(
            template_name, selected_models, selected_tests, selected_roles
        )
        
        # 保存配置
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_file = f"quick_config_{template_name}_{timestamp}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 配置已生成: {config_file}")
        print(f"   包含 {len(config['test_suites'][0]['tasks'])} 个测试任务")
        
        # 询问是否立即运行
        run_now = input("是否立即运行测试? (y/n): ").strip().lower()
        if run_now == 'y':
            self.run_batch(config_file)
    
    def quick_mode(self, template: str, models: List[str] = None, 
                  test_files: List[str] = None, roles: List[str] = None,
                  language: str = "en"):
        """快速模式 - 命令行参数"""
        models = models or self.get_available_models()[:2]  # 默认前2个模型
        test_files = test_files or self.get_available_test_files(language)[:1]
        roles = roles or ["default"]
        
        config = self.template_manager.generate_config(template, models, test_files, roles)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_file = f"quick_{template}_{timestamp}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 快速配置已生成: {config_file}")
        print(f"   模板: {template}")
        print(f"   任务数: {len(config['test_suites'][0]['tasks'])}")
        
        return config_file
    
    def run_batch(self, config_file: str):
        """运行批处理"""
        try:
            import subprocess
            cmd = [sys.executable, "run_batch_suite.py", config_file]
            print(f"运行命令: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"运行失败: {e}")
        except FileNotFoundError:
            print("未找到 run_batch_suite.py，请确保在当前目录")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="快速批处理配置生成器")
    parser.add_argument("--template", choices=["baseline", "stress_test", "context_test", 
                                              "full_matrix", "quick_validation", "temperature_sweep"],
                       help="使用预设模板")
    parser.add_argument("--models", nargs="+", help="指定模型")
    parser.add_argument("--tests", nargs="+", help="指定测试文件")
    parser.add_argument("--roles", nargs="+", help="指定角色")
    parser.add_argument("--language", choices=["en", "zh", "all"], default="en", help="语言选择")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    parser.add_argument("--run", action="store_true", help="生成后立即运行")
    
    args = parser.parse_args()
    
    generator = QuickBatchGenerator()
    
    if args.interactive or not any([args.template, args.models, args.tests, args.roles]):
        generator.interactive_mode()
    elif args.template:
        config_file = generator.quick_mode(
            args.template, args.models, args.tests, args.roles, args.language
        )
        if args.run:
            generator.run_batch(config_file)
    else:
        print("请使用 --interactive 进入交互模式，或指定 --template 参数")

if __name__ == "__main__":
    main()