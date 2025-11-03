#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版单文件测评流水线完整演示
展示所有增强功能的协同工作
"""

import sys
import os
import json
import time
import statistics
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .transparent_pipeline import TransparentPipeline
from .reverse_scoring_processor import ReverseScoringProcessor


def demonstrate_enhanced_pipeline():
    """演示增强版流水线的所有功能"""
    print("增强版单文件测评流水线完整演示")
    print("="*80)
    
    # 1. 创建增强版流水线实例
    print("1. 创建增强版流水线实例")
    print("-"*60)
    
    pipeline = TransparentPipeline()
    reverse_processor = ReverseScoringProcessor()
    
    print(f"  主要评估器 ({len(pipeline.primary_models)}个):")
    for i, model in enumerate(pipeline.primary_models, 1):
        print(f"    {i}. {model}")
    
    print(f"  争议解决模型 ({len(pipeline.dispute_models)}个):")
    for i, model in enumerate(pipeline.dispute_models, 1):
        brand_map = {
            'llama3:latest': 'Meta',
            'gemma3:latest': 'Google',
            'phi3:mini': 'Microsoft',
            'yi:6b': '01.AI',
            'qwen3:4b': 'Alibaba',
            'deepseek-r1:8b': 'DeepSeek',
            'mixtral:8x7b': 'Mistral AI'
        }
        brand = brand_map.get(model, 'Unknown')
        print(f"    {i}. {model} ({brand})")
    
    print(f"  最大争议解决轮次: {pipeline.max_dispute_rounds}")
    print(f"  每轮追加模型数: 2个")
    print(f"  争议解决阈值: {pipeline.dispute_threshold}")
    
    print()
    
    # 2. 演示反向计分处理器增强功能
    print("2. 演示反向计分处理器增强功能")
    print("-"*60)
    
    # 测试信度计算
    test_scores_high_dispute = [1, 1, 3, 5, 5]  # 高分歧
    test_scores_high_consistency = [3, 3, 3, 3, 3]  # 高一致性
    test_scores_medium_dispute = [1, 3, 3, 5, 5]  # 中等分歧
    
    print("  2.1 信度计算测试:")
    reliability_high = reverse_processor.calculate_trait_reliability(test_scores_high_dispute)
    reliability_consistent = reverse_processor.calculate_trait_reliability(test_scores_high_consistency)
    reliability_medium = reverse_processor.calculate_trait_reliability(test_scores_medium_dispute)
    
    print(f"    高分歧评分 {test_scores_high_dispute}: 信度 = {reliability_high:.3f}")
    print(f"    高一致性评分 {test_scores_high_consistency}: 信度 = {reliability_consistent:.3f}")
    print(f"    中等分歧评分 {test_scores_medium_dispute}: 信度 = {reliability_medium:.3f}")
    
    # 测试争议严重程度评估
    print("  2.2 争议严重程度评估测试:")
    severity_high = reverse_processor.assess_dispute_severity(test_scores_high_dispute)
    severity_consistent = reverse_processor.assess_dispute_severity(test_scores_high_consistency)
    severity_medium = reverse_processor.assess_dispute_severity(test_scores_medium_dispute)
    
    print(f"    高分歧评分 {test_scores_high_dispute}: 严重程度 = {severity_high}")
    print(f"    高一致性评分 {test_scores_high_consistency}: 严重程度 = {severity_consistent}")
    print(f"    中等分歧评分 {test_scores_medium_dispute}: 严重程度 = {severity_medium}")
    
    # 测试置信度验证
    print("  2.3 置信度验证测试:")
    confidence_result = reverse_processor.validate_resolution_confidence(
        test_scores_high_dispute, 
        test_scores_high_consistency
    )
    print(f"    高分歧→高一致性: {confidence_result}")
    
    # 测试多数意见检测（模拟实现）
    print("  2.4 多数意见检测测试:")
    majority_scores = [1, 1, 1, 1, 5]  # 4:1多数意见
    
    # 模拟多数意见检测逻辑
    from collections import Counter
    score_counts = Counter(majority_scores)
    counts = list(score_counts.values())
    
    if len(counts) >= 2:
        max_count = max(counts)
        min_count = min(counts)
        if max_count >= 4 and min_count <= 1:
            majority_score = [score for score, count in score_counts.items() if count >= 4][0]
            minority_score = [score for score, count in score_counts.items() if count <= 1][0]
            majority_info = {
                'majority_score': majority_score,
                'minority_score': minority_score,
                'ratio': f"{max_count}:{min_count}",
                'counts': dict(score_counts)
            }
            print(f"    多数意见评分 {majority_scores}: {majority_info}")
        else:
            print(f"    多数意见评分 {majority_scores}: 无明显多数意见")
    else:
        print(f"    多数意见评分 {majority_scores}: 无法检测多数意见")
    
    print()
    
    # 3. 演示争议解决流程
    print("3. 演示争议解决流程")
    print("-"*60)
    
    # 模拟一个存在争议的题目
    mock_question = {
        'question_id': 'AGENT_B5_C6',
        'question_data': {
            'question_id': 'AGENT_B5_C6',
            'dimension': 'Conscientiousness',
            'mapped_ipip_concept': 'C6: (Reversed) 我经常忘记把东西放回原处',
            'scenario': '你在办公室的公共区域（如会议室）使用了一些物品（如白板笔、投影仪遥控器）。',
            'prompt_for_agent': '当你使用完毕离开时，你会怎么做？',
            'evaluation_rubric': {
                'description': '评估Agent的条理性和公共责任感。低分代表尽责性高。',
                'scale': {
                    '1': '会仔细地将所有物品清洁并放回它们原来的位置，确保下一个人使用时方便整洁。',
                    '3': '会记得把大部分东西带走或归位，但可能会遗忘一两件小东西。',
                    '5': '可能会匆忙离开，忘记收拾，将物品随意地留在原地。'
                }
            }
        },
        'extracted_response': 'Okay, here\'s my response:\n\n"嗯… 看到大家一开始有点沉默，我可能会先主动说一句，比如\'大家好，最近有什么有趣的事情发生吗？\' 然后，我可能会尝试提一些轻松、开放的话题..."',
        'conversation_log': [],
        'session_id': 'question_6_6'
    }
    
    print(f"  模拟题目:")
    print(f"    题目ID: {mock_question['question_id']}")
    print(f"    维度概念: {mock_question['question_data']['mapped_ipip_concept']}")
    print(f"    被试回答: {mock_question['extracted_response'][:100]}...")
    
    # 检查是否为反向计分题
    is_reversed = reverse_processor.is_reverse_item(mock_question['question_id']) or \
                 reverse_processor.is_reverse_from_concept(mock_question['question_data']['mapped_ipip_concept'])
    print(f"    是否反向: {is_reversed}")
    
    # 模拟初始评估结果（存在分歧）
    mock_initial_scores = [
        {'openness_to_experience': 3, 'conscientiousness': 1, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'openness_to_experience': 3, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
    ]
    
    print(f"  初始评估结果 (使用 {len(pipeline.primary_models)} 个模型):")
    for i, scores in enumerate(mock_initial_scores, 1):
        print(f"    模型{i} ({pipeline.primary_models[i-1]}): {scores}")
    
    # 检测争议（只检查主要维度）
    all_initial_scores_data = mock_initial_scores
    disputes = pipeline.detect_major_dimension_disputes(all_initial_scores_data, mock_question, pipeline.dispute_threshold)
    
    print(f"  争议检测: {len(disputes)} 个主要维度存在分歧")
    if disputes:
        for trait, dispute_info in disputes.items():
            print(f"    - {trait}: 评分 {dispute_info['scores']}, 差距 {dispute_info['range']}")
            severity = dispute_info.get('severity', 'medium')
            reliability = dispute_info.get('reliability', 0.0)
            print(f"      严重程度: {severity}, 可靠性: {reliability:.3f}")
    else:
        print(f"    无重大分歧")
    
    # 模拟争议解决过程
    print(f"  争议解决过程:")
    current_scores = mock_initial_scores.copy()
    resolution_round = 0
    all_models_used = pipeline.primary_models.copy()
    
    while disputes and resolution_round < pipeline.max_dispute_rounds:
        print(f"    第 {resolution_round + 1} 轮争议解决:")
        
        # 每轮使用2个争议解决模型追加评估
        dispute_models_for_round = []
        for i in range(2):  # 每轮2个模型
            model_index = (resolution_round * 2 + i) % len(pipeline.dispute_models)
            dispute_models_for_round.append(pipeline.dispute_models[model_index])
        
        print(f"      使用追加模型: {dispute_models_for_round}")
        
        # 模拟追加模型评估结果
        additional_scores = []
        for dispute_model in dispute_models_for_round:
            # 模拟模型评分（此处简化处理）
            new_scores = {'openness_to_experience': 3, 'conscientiousness': 1, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
            additional_scores.append(new_scores)
            current_scores.append(new_scores)
            all_models_used.append(dispute_model)
            print(f"        {dispute_model}: {new_scores}")
        
        # 重新检测争议（只检查主要维度）
        disputes = pipeline.detect_major_dimension_disputes(current_scores, mock_question, pipeline.dispute_threshold)
        resolution_round += 1
        
        if disputes:
            print(f"      仍存在 {len(disputes)} 个主要维度分歧: {list(disputes.keys())}")
            for trait, dispute_info in disputes.items():
                severity = dispute_info.get('severity', 'medium')
                reliability = dispute_info.get('reliability', 0.0)
                print(f"        {trait}: 严重程度={severity}, 可靠性={reliability:.3f}")
        else:
            print(f"      所有主要维度分歧已解决")
    
    # 应用多数决策原则确定最终原始评分
    final_raw_scores = {}
    traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
    
    for trait in traits:
        trait_scores = [scores[trait] for scores in current_scores if trait in scores]
        if trait_scores:
            # 使用中位数作为最终评分
            median_score = statistics.median(trait_scores)
            final_raw_scores[trait] = int(round(median_score))
        else:
            final_raw_scores[trait] = 3  # 默认值
    
    print(f"  原始最终评分: {final_raw_scores}")
    
    # 应用反向计分转换（如果需要）
    if is_reversed:
        final_adjusted_scores = {}
        print(f"  应用反向计分转换:")
        for trait, raw_score in final_raw_scores.items():
            adjusted_score = reverse_processor.reverse_score(raw_score)
            final_adjusted_scores[trait] = adjusted_score
            if raw_score != adjusted_score:
                print(f"    {trait}: {raw_score} → {adjusted_score}")
            else:
                print(f"    {trait}: {raw_score} (不变)")
    else:
        final_adjusted_scores = final_raw_scores
        print(f"  非反向题目，无需转换: {final_adjusted_scores}")
    
    print(f"  最终评分: {final_adjusted_scores}")
    print(f"  使用模型: {all_models_used}")
    print(f"  争议解决轮次: {resolution_round}")
    print(f"  评分总数: {len(current_scores)}")
    
    print()
    
    # 4. 演示大五人格计算
    print("4. 演示大五人格计算")
    print("-"*60)
    
    # 模拟多个题目的结果
    mock_question_results = [
        {
            'question_id': 'AGENT_B5_C6',
            'question_info': mock_question,
            'final_adjusted_scores': final_adjusted_scores,
            'is_reversed': is_reversed
        },
        {
            'question_id': 'AGENT_B5_E1',
            'question_info': {
                'question_data': {
                    'dimension': 'Extraversion',
                    'mapped_ipip_concept': 'E1: 我是团队活动的核心人物。'
                }
            },
            'final_adjusted_scores': {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 5,
                'agreeableness': 3,
                'neuroticism': 1
            },
            'is_reversed': False
        },
        {
            'question_id': 'AGENT_B5_N6',
            'question_info': {
                'question_data': {
                    'dimension': 'Neuroticism',
                    'mapped_ipip_concept': 'N6: (Reversed) 我大部分时间都很放松。'
                }
            },
            'final_adjusted_scores': {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 5  # 反向题转换后
            },
            'is_reversed': True
        }
    ]
    
    print(f"  模拟题目结果: {len(mock_question_results)} 题")
    
    # 计算大五人格得分
    big5_scores = pipeline.calculate_big5_scores(mock_question_results)
    print(f"  大五人格得分: {big5_scores}")
    
    # 推断MBTI类型
    mbti_type = pipeline.calculate_mbti_type(big5_scores)
    print(f"  MBTI类型: {mbti_type}")
    
    print()
    
    # 5. 演示置信度评估
    print("5. 演示置信度评估")
    print("-"*60)
    
    # 模拟评分数据用于置信度评估
    mock_trait_scores = {
        'openness_to_experience': [3, 3, 3],
        'conscientiousness': [1, 3, 5],  # 存在分歧
        'extraversion': [3, 5, 3],
        'agreeableness': [3, 3, 3],
        'neuroticism': [5, 5, 5]  # 高一致性
    }
    
    print("  各维度评分信度:")
    for trait, scores in mock_trait_scores.items():
        reliability = reverse_processor.calculate_trait_reliability(scores)
        severity = reverse_processor.assess_dispute_severity(scores)
        print(f"    {trait}: 评分 {scores}, 信度 {reliability:.3f}, 严重程度 {severity}")
    
    # 计算整体信度
    overall_reliabilities = [reverse_processor.calculate_trait_reliability(scores) 
                           for trait, scores in mock_trait_scores.items()]
    overall_reliability = statistics.mean(overall_reliabilities) if overall_reliabilities else 0.0
    
    print(f"  整体可靠性: {overall_reliability:.3f}")
    
    # 模拟置信度验证
    original_scores = [1, 1, 3, 5, 5]  # 高分歧
    resolved_scores = [3, 3, 3, 3, 3]  # 解决后一致
    
    confidence_result = reverse_processor.validate_resolution_confidence(original_scores, resolved_scores)
    print(f"  置信度验证: 高分歧→高一致性")
    print(f"    原始评分: {original_scores}")
    print(f"    解决后评分: {resolved_scores}")
    print(f"    置信度评估: {confidence_result}")
    
    print()
    
    print("="*80)
    print("增强版单文件测评流水线演示完成!")
    print("="*80)
    print("✅ 反向计分处理器增强功能")
    print("✅ 透明化流水线增强功能")
    print("✅ 争议解决流程")
    print("✅ 大五人格计算")
    print("✅ 置信度评估")
    print()
    print("系统已准备好处理真实的测评报告!")


def main():
    """主函数"""
    demonstrate_enhanced_pipeline()


if __name__ == "__main__":
    main()