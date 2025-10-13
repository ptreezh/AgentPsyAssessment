#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本用于验证Ollama评估器功能
"""

import json
import sys
import os
import io

# 确保在Windows上使用UTF-8编码
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_segmented_analysis import OllamaEvaluator

def test_ollama_connection():
    """测试Ollama连接"""
    print("测试Ollama连接...")
    evaluator = OllamaEvaluator()
    is_connected = evaluator.check_connection()
    print(f"连接状态: {is_connected}")
    
    if is_connected:
        models = evaluator.list_models()
        model_count = len(models.get('models', []))
        print(f"可用模型数量: {model_count}")
        if model_count > 0:
            print("前5个模型:")
            for i, model in enumerate(models['models'][:5]):
                print(f"  {i+1}. {model['name']}")
        return True
    else:
        print("无法连接到Ollama服务，请确保服务正在运行")
        return False

if __name__ == "__main__":
    test_ollama_connection()