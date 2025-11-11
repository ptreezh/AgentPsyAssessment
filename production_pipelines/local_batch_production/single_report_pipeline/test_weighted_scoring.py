#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重计算测试脚本
验证大五人格评分中的权重机制
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .transparent_pipeline import TransparentPipeline
from .reverse_scoring_processor import ReverseScoringProcessor


def test_weighted_scoring():
    """测试加权评分机制"""
    print("测试加权评分机制")
    print("="*60)
    
    # 创建处理器实例
    pipeline = TransparentPipeline()
    reverse_processor = ReverseScoringProcessor()
    
    # 模拟处理结果（包含主要维度和其他维度评分）
    mock_results = [
        {
            'question_id': 'AGENT_B5_C6',
            'final_adjusted_scores': {
                'openness_to_experience': 3,      # 其他维度评分
                'conscientiousness': 5,            # 主要维度评分（高）
                'extraversion': 3,                 # 其他维度评分
                'agreeableness': 3,                # 其他维度评分
                'neuroticism': 3                   # 其他维度评分
            },
            'question_info': {
                'question_data': {
                    'dimension': 'Conscientiousness'  # 主要维度
                }
            },
            'is_reversed': True
        },
        {
            'question_id': 'AGENT_B5_E1',
            'final_adjusted_scores': {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 5,                 # 主要维度评分（高）
                'agreeableness': 3,
                'neuroticism': 1                   # 其他维度评分（低）
            },
            'question_info': {
                'question_data': {
                    'dimension': 'Extraversion'    # 主要维度
                }
            },
            'is_reversed': False
        }
    ]
    
    print("模拟处理结果:")
    for i, result in enumerate(mock_results, 1):
        primary_dim = result['question_info']['question_data']['dimension']
        scores = result['final_adjusted_scores']
        print(f"  第{i}题 ({result['question_id']}) - 主要维度: {primary_dim}")
        print(f"    评分: {scores}")
    
    print("\n使用透明化流水线计算加权得分:")
    weighted_scores = pipeline.calculate_big5_scores(mock_results)
    print(f"加权大五得分: {weighted_scores}")
    
    print("\n使用反向计分处理器计算加权得分:")
    reverse_weighted_scores = reverse_processor.calculate_big5_scores(mock_results)
    print(f"反向处理器加权得分: {reverse_weighted_scores}")
    
    # 验证权重计算逻辑
    print("\n权重计算验证:")
    print("权重分配规则:")
    print("  - 主要维度: 70% 权重")
    print("  - 其他维度: 各 7.5% 权重")
    print()
    
    # 详细分析第一题
    print("第一题详细分析 (主要维度: Conscientiousness):")
    q1_scores = mock_results[0]['final_adjusted_scores']
    print(f"  Conscientiousness (主要): {q1_scores['conscientiousness']} × 0.7 = {q1_scores['conscientiousness'] * 0.7}")
    print(f"  Openness: {q1_scores['openness_to_experience']} × 0.075 = {q1_scores['openness_to_experience'] * 0.075}")
    print(f"  Extraversion: {q1_scores['extraversion']} × 0.075 = {q1_scores['extraversion'] * 0.075}")
    print(f"  Agreeableness: {q1_scores['agreeableness']} × 0.075 = {q1_scores['agreeableness'] * 0.075}")
    print(f"  Neuroticism: {q1_scores['neuroticism']} × 0.075 = {q1_scores['neuroticism'] * 0.075}")
    
    total_weighted = (q1_scores['conscientiousness'] * 0.7 + 
                     q1_scores['openness_to_experience'] * 0.075 +
                     q1_scores['extraversion'] * 0.075 +
                     q1_scores['agreeableness'] * 0.075 +
                     q1_scores['neuroticism'] * 0.075)
    total_weight = 0.7 + 0.075 * 4
    avg_weighted = total_weighted / total_weight
    
    print(f"  加权总和: {total_weighted:.3f}")
    print(f"  权重总和: {total_weight:.3f}")
    print(f"  加权平均: {avg_weighted:.3f}")
    
    print("\n权重机制优势:")
    print("1. 突出主要维度贡献")
    print("2. 保留其他维度信息")
    print("3. 提高评估准确性")
    print("4. 符合专业测评标准")


def compare_weighted_vs_equal():
    """比较加权vs平等评分"""
    print("\n加权vs平等评分比较")
    print("="*60)
    
    # 模拟极端情况：主要维度得分很高，其他维度得分很低
    extreme_results = [
        {
            'question_id': 'AGENT_B5_C6',
            'final_adjusted_scores': {
                'openness_to_experience': 1,       # 极低
                'conscientiousness': 5,             # 极高（主要维度）
                'extraversion': 1,                 # 极低
                'agreeableness': 1,                # 极低
                'neuroticism': 1                   # 极低
            },
            'question_info': {
                'question_data': {
                    'dimension': 'Conscientiousness'
                }
            },
            'is_reversed': True
        }
    ]
    
    pipeline = TransparentPipeline()
    
    print("极端情况测试:")
    print("主要维度: 5分 (极高)")
    print("其他维度: 1分 (极低)")
    
    # 加权评分
    weighted_scores = pipeline.calculate_big5_scores(extreme_results)
    conscientiousness_weighted = weighted_scores['conscientiousness']
    
    # 平等评分（模拟）
    equal_avg = (1 + 5 + 1 + 1 + 1) / 5  # 平均分
    conscientiousness_equal = equal_avg
    
    print(f"\n结果比较:")
    print(f"  加权评分 Conscientiousness: {conscientiousness_weighted}")
    print(f"  平等评分 Conscientiousness: {conscientiousness_equal}")
    print(f"  差异: {conscientiousness_weighted - conscientiousness_equal:.2f}")
    
    print(f"\n结论: 加权评分更好地反映了主要维度的高特质水平")


if __name__ == "__main__":
    test_weighted_scoring()
    compare_weighted_vs_equal()