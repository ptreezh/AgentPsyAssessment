#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析配置文件
定义批量分析的各种参数和设置
"""

import os
from pathlib import Path


class BatchConfig:
    """批量分析配置"""
    
    def __init__(self):
        # 默认目录设置
        self.default_input_dir = Path("../results/readonly-original")
        self.default_output_dir = Path("../results/batch-analysis-results")
        
        # 模型配置
        self.primary_models = [
            'qwen3:8b',           # Alibaba
            'deepseek-r1:8b',     # DeepSeek 
            'mistral-nemo:latest' # Mistral AI
        ]
        
        self.dispute_models = [
            'llama3:latest',      # Meta (第1轮第1个)
            'gemma3:latest',      # Google (第1轮第2个)
            'phi3:mini',          # Microsoft (第2轮第1个)
            'yi:6b',              # 01.AI (第2轮第2个)
            'qwen3:4b',           # Alibaba (第3轮第1个)
            'deepseek-r1:8b',     # DeepSeek (第3轮第2个)
            'mixtral:8x7b'        # Mistral AI (备用)
        ]
        
        # 处理参数
        self.max_dispute_rounds = 3      # 最大争议解决轮次
        self.models_per_round = 2        # 每轮追加模型数
        self.dispute_threshold = 1.0     # 争议检测阈值
        self.checkpoint_interval = 5     # 检查点间隔
        
        # 文件处理参数
        self.file_pattern = "*.json"     # 文件匹配模式
        self.max_files_per_run = None    # 每次运行最大文件数 (None表示无限制)
        self.resume_enabled = True       # 启用断点续跑
        
        # 性能参数
        self.delay_between_files = 1     # 文件间延迟(秒)
        self.delay_between_models = 0.5  # 模型间延迟(秒)
        self.max_retries = 3             # 最大重试次数
        self.retry_delay = 20            # 重试延迟(秒)
        
        # 输出配置
        self.save_detailed_logs = True   # 保存详细日志
        self.save_intermediate_results = True  # 保存中间结果
        self.generate_summary_report = True    # 生成摘要报告
    
    def get_model_brands(self) -> dict:
        """
        获取模型品牌映射
        
        Returns:
            模型品牌映射字典
        """
        return {
            'qwen3:8b': 'Alibaba',
            'deepseek-r1:8b': 'DeepSeek',
            'mistral-nemo:latest': 'Mistral AI',
            'llama3:latest': 'Meta',
            'gemma3:latest': 'Google',
            'phi3:mini': 'Microsoft',
            'yi:6b': '01.AI',
            'qwen3:4b': 'Alibaba',
            'mixtral:8x7b': 'Mistral AI'
        }
    
    def validate_model_availability(self) -> dict:
        """
        验证模型可用性
        
        Returns:
            模型可用性状态
        """
        import ollama
        
        model_status = {}
        
        # 检查所有模型
        all_models = self.primary_models + self.dispute_models
        unique_models = list(set(all_models))  # 去重
        
        for model in unique_models:
            try:
                # 尝试获取模型信息
                response = ollama.list()
                available_models = [m['name'] for m in response.get('models', [])]
                model_status[model] = model in available_models
            except Exception as e:
                model_status[model] = False
                print(f"⚠️  检查模型 {model} 可用性失败: {e}")
        
        return model_status
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("批量分析配置摘要")
        print("="*60)
        print(f"输入目录: {self.default_input_dir}")
        print(f"输出目录: {self.default_output_dir}")
        print(f"文件匹配模式: {self.file_pattern}")
        print()
        print("模型配置:")
        print(f"  主要评估器 ({len(self.primary_models)}个):")
        for i, model in enumerate(self.primary_models, 1):
            brand = self.get_model_brands().get(model, 'Unknown')
            print(f"    {i}. {model} ({brand})")
        print(f"  争议解决模型 ({len(self.dispute_models)}个):")
        for i, model in enumerate(self.dispute_models, 1):
            brand = self.get_model_brands().get(model, 'Unknown')
            print(f"    {i}. {model} ({brand})")
        print()
        print("处理参数:")
        print(f"  最大争议解决轮次: {self.max_dispute_rounds}")
        print(f"  每轮追加模型数: {self.models_per_round}")
        print(f"  争议检测阈值: {self.dispute_threshold}")
        print(f"  检查点间隔: 每 {self.checkpoint_interval} 个文件")
        print()
        print("文件处理参数:")
        print(f"  文件匹配模式: {self.file_pattern}")
        print(f"  每次运行最大文件数: {self.max_files_per_run or '无限制'}")
        print(f"  启用断点续跑: {'是' if self.resume_enabled else '否'}")
        print()
        print("性能参数:")
        print(f"  文件间延迟: {self.delay_between_files} 秒")
        print(f"  模型间延迟: {self.delay_between_models} 秒")
        print(f"  最大重试次数: {self.max_retries}")
        print(f"  重试延迟: {self.retry_delay} 秒")
        print()
        print("输出配置:")
        print(f"  保存详细日志: {'是' if self.save_detailed_logs else '否'}")
        print(f"  保存中间结果: {'是' if self.save_intermediate_results else '否'}")
        print(f"  生成摘要报告: {'是' if self.generate_summary_report else '否'}")


def main():
    """主函数 - 显示配置信息"""
    config = BatchConfig()
    config.print_config_summary()
    
    # 验证模型可用性
    print("\n验证模型可用性:")
    print("-"*60)
    model_status = config.validate_model_availability()
    
    available_count = sum(1 for status in model_status.values() if status)
    total_count = len(model_status)
    
    print(f"可用模型: {available_count}/{total_count}")
    for model, status in model_status.items():
        brand = config.get_model_brands().get(model, 'Unknown')
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {model} ({brand})")
    
    if available_count < total_count:
        print(f"\n⚠️  警告: {total_count - available_count} 个模型不可用")
        print("请确保所有必需模型都已下载并可在Ollama中使用")


if __name__ == "__main__":
    main()