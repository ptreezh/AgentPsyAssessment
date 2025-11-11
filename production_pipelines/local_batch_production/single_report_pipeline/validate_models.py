#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型验证脚本
验证本地可用的模型是否符合项目要求（>3B参数，不同品牌）
"""

import subprocess
import yaml
import re
from typing import List, Dict, Tuple


def get_local_models():
    """获取本地可用的Ollama模型"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
        
        models = []
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    size_str = parts[2] if parts[2] != '-' else "Unknown"
                    models.append({
                        'name': name,
                        'size_str': size_str,
                        'size_gb': parse_size_gb(size_str)
                    })
        return models
    except subprocess.CalledProcessError:
        print("错误：无法运行 ollama list 命令")
        return []


def parse_size_gb(size_str: str) -> float:
    """解析模型大小字符串为GB数值"""
    if size_str == "-" or size_str == "Unknown":
        return 0.0
    
    # 提取数值和单位
    match = re.search(r'([\d.]+)\s*(\w+)', size_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()
        
        if 'gb' in unit or 'g' == unit:
            return value
        elif 'mb' in unit or 'm' == unit:
            return value / 1024.0
        elif 'kb' in unit or 'k' == unit:
            return value / (1024.0 * 1024.0)
        elif 'b' == unit:
            return value / (1024.0 * 1024.0 * 1024.0)
    
    # 如果格式不匹配，尝试直接转换为浮点数（假设单位是GB）
    try:
        return float(size_str)
    except ValueError:
        return 0.0


def filter_models_by_size(models: List[Dict], min_size_gb: float = 3.0) -> List[Dict]:
    """根据大小过滤模型"""
    return [model for model in models if model['size_gb'] >= min_size_gb]


def get_brand_from_model_name(model_name: str) -> str:
    """从模型名称中提取品牌信息"""
    model_name_lower = model_name.lower()
    
    brand_mapping = {
        'qwen': 'Alibaba',
        'gemma': 'Google',
        'llama': 'Meta',
        'mistral': 'Mistral AI',
        'deepseek': 'DeepSeek',
        'yi': '01.AI',
        'glm': 'Zhipu AI',
        'phi': 'Microsoft',
        'yi': '01.AI',
        'command': 'Cohere',
        'llm': 'Unknown'
    }
    
    for keyword, brand in brand_mapping.items():
        if keyword in model_name_lower:
            return brand
    
    return 'Unknown'


def select_diverse_models(models: List[Dict], count: int = 3) -> List[Dict]:
    """选择不同品牌的模型"""
    selected = []
    used_brands = set()
    
    for model in models:
        brand = get_brand_from_model_name(model['name'])
        if brand not in used_brands and len(selected) < count:
            model['brand'] = brand
            selected.append(model)
            used_brands.add(brand)
    
    return selected


def main():
    print("🔍 检查本地Ollama模型...")
    
    # 获取所有本地模型
    all_models = get_local_models()
    
    if not all_models:
        print("❌ 未找到任何本地模型")
        return
    
    print(f"📋 发现 {len(all_models)} 个本地模型:")
    for model in all_models:
        print(f"  - {model['name']} ({model['size_str']})")
    
    # 过滤出>3B参数的模型
    large_models = filter_models_by_size(all_models, 3.0)
    print(f"\n📊 符合>3B参数要求的模型 ({len(large_models)} 个):")
    for model in large_models:
        brand = get_brand_from_model_name(model['name'])
        print(f"  - {model['name']} ({model['size_str']}, {brand})")
    
    if len(large_models) < 3:
        print(f"\n❌ 错误: 只找到 {len(large_models)} 个符合>3B参数要求的模型，需要至少3个")
        return
    
    # 选择不同品牌的模型
    diverse_models = select_diverse_models(large_models, 3)
    print(f"\n🎯 选择的3个不同品牌模型:")
    for i, model in enumerate(diverse_models, 1):
        print(f"  {i}. {model['name']} ({model['size_str']}, {model['brand']})")
    
    if len(diverse_models) < 3:
        print(f"\n❌ 错误: 只找到 {len(diverse_models)} 个不同品牌的>3B模型，需要3个")
        print("💡 建议: 安装更多不同品牌的>3B参数模型")
        
        # 显示所有可用的>3B模型
        print(f"\n📋 所有符合>3B参数要求的模型:")
        for i, model in enumerate(large_models, 1):
            brand = get_brand_from_model_name(model['name'])
            status = "✓" if brand not in [m['brand'] for m in diverse_models] else "✗ (品牌重复)"
            print(f"  {i}. {model['name']} ({model['size_str']}, {brand}) {status}")
        
        return
    
    print(f"\n✅ 模型验证成功！可以使用以下模型组合:")
    print("  主要评估器:")
    for model in diverse_models:
        print(f"    - {model['name']} ({model['brand']})")
    
    # 检查争议解决模型
    dispute_models = [m for m in diverse_models if m not in diverse_models[:3]]
    if len(dispute_models) < 2:
        # 从所有>3B模型中选择2个额外模型
        dispute_candidates = [m for m in large_models if m not in diverse_models]
        dispute_models = dispute_candidates[:2]
    
    print("  争议解决模型:")
    for model in dispute_models[:2]:
        brand = get_brand_from_model_name(model['name'])
        model['brand'] = brand
        print(f"    - {model['name']} ({model['brand']})")
    
    print(f"\n📝 建议将以下配置更新到 config.yaml:")
    print("  models:")
    print("    primary_models:")
    for model in diverse_models:
        print(f"      - \"{model['name']}\"  # {model['brand']}")
    print("    dispute_resolution_models:")
    for model in dispute_models[:2]:
        print(f"      - \"{model['name']}\"  # {model['brand']}")
    
    # 保存配置到文件
    if len(dispute_models) >= 2:
        config = {
            'pipeline': {
                'models': {
                    'primary_count': 3,
                    'primary_models': [m['name'] for m in diverse_models],
                    'dispute_resolution_models': [m['name'] for m in dispute_models[:2]],
                    'min_parameter_size': '3b',
                    'selection_strategy': 'diverse_brands'
                },
                'dispute_resolution': {
                    'initial_threshold': 1.0,
                    'max_rounds': 3,
                    'additional_evaluators_per_round': 2
                },
                'scoring': {
                    'scale': [1, 3, 5],
                    'consistency_threshold': 0.8
                },
                'output': {
                    'include_detailed_logs': True,
                    'confidence_calculation': True
                }
            }
        }
        
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"\n💾 配置已保存到 config.yaml")


if __name__ == "__main__":
    main()