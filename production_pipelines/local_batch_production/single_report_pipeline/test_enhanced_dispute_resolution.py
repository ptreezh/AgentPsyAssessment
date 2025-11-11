#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
争议解决机制测试脚本
验证增强的信度验证和分层争议解决策略
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .transparent_pipeline import TransparentPipeline
from .reverse_scoring_processor import ReverseScoringProcessor


def test_enhanced_dispute_resolution():
    """测试增强的争议解决机制"""
    print("增强争议解决机制测试")
    print("="*60)
    
    # 创建处理器实例
    pipeline = TransparentPipeline()
    processor = ReverseScoringProcessor()
    
    print("1. 信度计算测试:")
    test_cases = [
        ([1, 1, 3, 5, 5], "高分歧评分"),
        ([3, 3, 3, 3, 3], "高一致性评分"),
        ([1, 3, 3, 5, 5], "中等分歧评分"),
        ([2, 3, 4, 4, 5], "连续型评分")
    ]
    
    for scores, description in test_cases:
        reliability = processor.calculate_trait_reliability(scores)
        severity = processor.assess_dispute_severity(scores)
        print(f"  {description} {scores}:")
        print(f"    信度 = {reliability:.3f}")
        print(f"    严重程度 = {severity}")
    
    print("\n2. 置信度验证测试:")
    # 模拟争议解决前后的情况
    original_scores = [1, 1, 3, 5, 5]  # 高分歧
    resolved_scores = [3, 3, 3, 3, 3]  # 解决后一致
    
    confidence_result = processor.validate_resolution_confidence(original_scores, resolved_scores)
    print(f"  原始评分: {original_scores}")
    print(f"  解决后评分: {resolved_scores}")
    print(f"  置信度评估: {confidence_result}")
    
    # 测试改进较小的情况
    slightly_improved_scores = [2, 2, 3, 4, 4]
    confidence_result_2 = processor.validate_resolution_confidence(original_scores, slightly_improved_scores)
    print(f"\n  原始评分: {original_scores}")
    print(f"  轻微改进评分: {slightly_improved_scores}")
    print(f"  置信度评估: {confidence_result_2}")
    
    print("\n3. 流水线集成测试:")
    # 模拟流水线中的争议检测
    mock_scores_list = [
        {'extraversion': 1, 'conscientiousness': 3, 'openness_to_experience': 5},
        {'extraversion': 3, 'conscientiousness': 3, 'openness_to_experience': 3},
        {'extraversion': 5, 'conscientiousness': 5, 'openness_to_experience': 1}
    ]
    
    # 检测所有维度争议
    all_disputes = pipeline.detect_disputes(mock_scores_list, 1.0)
    print(f"  所有维度争议检测:")
    for trait, dispute_info in all_disputes.items():
        scores = dispute_info['scores']
        reliability = processor.calculate_trait_reliability(scores)
        severity = processor.assess_dispute_severity(scores)
        print(f"    {trait}: 评分 {scores}, 可靠性 {reliability:.3f}, 严重程度 {severity}")
    
    # 模拟题目主要维度
    mock_question = {
        'question_data': {
            'dimension': 'Extraversion'
        }
    }
    
    # 检测主要维度争议
    major_disputes = pipeline.detect_major_dimension_disputes(mock_scores_list, mock_question, 1.0)
    print(f"\n  主要维度争议检测:")
    for trait, dispute_info in major_disputes.items():
        scores = dispute_info['scores']
        reliability = processor.calculate_trait_reliability(scores)
        severity = processor.assess_dispute_severity(scores)
        print(f"    {trait}: 评分 {scores}, 可靠性 {reliability:.3f}, 严重程度 {severity}")
    
    print("\n增强争议解决机制测试完成!")


def main():
    """主函数"""
    test_enhanced_dispute_resolution()


if __name__ == "__main__":
    main()