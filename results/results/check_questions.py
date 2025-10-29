#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查评估文件中的问题数量
"""

import json
import sys
import io

# 确保在Windows上使用UTF-8编码
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_question_count(file_path):
    """检查JSON文件中的问题数量"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取问题列表
        assessment_results = data.get('assessment_results', [])
        print(f"文件 {file_path} 中的问题数量: {len(assessment_results)}")
        
        # 显示前几个问题的示例
        print("\n前3个问题的示例:")
        for i in range(min(3, len(assessment_results))):
            result = assessment_results[i]
            question_data = result.get('question_data', {})
            print(f"  问题 {i+1}:")
            print(f"    ID: {question_data.get('question_id', 'N/A')}")
            print(f"    维度: {question_data.get('dimension', 'N/A')}")
            print(f"    场景: {question_data.get('scenario', 'N/A')[:100]}...")
            print()
            
    except Exception as e:
        print(f"读取文件时出错: {e}")

if __name__ == "__main__":
    check_question_count("asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json")