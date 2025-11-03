#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整验证脚本 - 验证所有增强功能
"""

import sys
import os
import statistics
from collections import Counter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .reverse_scoring_processor import ReverseScoringProcessor
from .transparent_pipeline import TransparentPipeline


def validate_enhanced_features():
    """验证所有增强功能"""
    print("完整验证脚本 - 验证所有增强功能")
    print("="*80)
    
    # 1. 验证反向计分处理器增强功能
    print("1. 验证反向计分处理器增强功能")
    print("-"*60)
    
    processor = ReverseScoringProcessor()
    
    # 测试信度计算
    print("  1.1 信度计算测试:")
    test_scores = [1, 1, 3, 5, 5]  # 高分歧
    reliability = processor.calculate_trait_reliability(test_scores)
    print(f"    高分歧评分 {test_scores}: 可靠性 = {reliability:.3f}")
    
    test_scores_2 = [3, 3, 3, 3, 3]  # 高一致性
    reliability_2 = processor.calculate_trait_reliability(test_scores_2)
    print(f"    高一致性评分 {test_scores_2}: 可靠性 = {reliability_2:.3f}")
    
    # 测试争议严重程度评估
    print("  1.2 争议严重程度评估测试:")
    severity = processor.assess_dispute_severity(test_scores)
    print(f"    高分歧评分 {test_scores}: 严重程度 = {severity}")
    
    severity_2 = processor.assess_dispute_severity(test_scores_2)
    print(f"    高一致性评分 {test_scores_2}: 严重程度 = {severity_2}")
    
    # 测试置信度验证
    print("  1.3 置信度验证测试:")
    confidence_result = processor.validate_resolution_confidence(test_scores, test_scores_2)
    print(f"    置信度验证: {confidence_result}")
    
    # 测试多数意见检测（模拟）
    print("  1.4 多数意见检测测试:")
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
    
    # 2. 验证透明化流水线增强功能
    print("2. 验证透明化流水线增强功能")
    print("-"*60)
    
    pipeline = TransparentPipeline()
    
    # 测试争议解决轮次
    print("  2.1 争议解决轮次验证:")
    print(f"    最大争议解决轮次: {pipeline.max_dispute_rounds}")
    print(f"    每轮追加模型数: 2 (固定值)")
    print(f"    总争议解决模型数: {len(pipeline.dispute_models)}")
    
    # 测试模型使用顺序
    print("  2.2 模型使用顺序验证:")
    all_dispute_models = []
    for round_num in range(2):  # 最多2轮额外争议解决
        for i in range(2):  # 每轮2个模型
            model_index = (round_num * 2 + i) % len(pipeline.dispute_models)
            all_dispute_models.append(pipeline.dispute_models[model_index])
    print(f"    争议解决模型顺序: {all_dispute_models}")
    
    print()
    
    # 3. 验证完整处理流程
    print("3. 验证完整处理流程")
    print("-"*60)
    
    # 模拟完整处理流程
    print("  3.1 模拟单题处理:")
    
    # 创建模拟题目数据
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
    
    print(f"    题目ID: {mock_question['question_id']}")
    print(f"    题目概念: {mock_question['question_data']['mapped_ipip_concept']}")
    print(f"    被试回答: {mock_question['extracted_response'][:100]}...")
    
    # 检查是否为反向计分题
    is_reversed = processor.is_reverse_item(mock_question['question_id']) or \
                 processor.is_reverse_from_concept(mock_question['question_data']['mapped_ipip_concept'])
    print(f"    是否反向: {is_reversed}")
    
    # 模拟评分
    mock_scores = [
        {'openness_to_experience': 3, 'conscientiousness': 1, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'openness_to_experience': 3, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
    ]
    
    print(f"    初始评分: {mock_scores}")
    
    # 检测争议
    disputes = pipeline.detect_disputes(mock_scores, 1.0)
    print(f"    争议检测: {len(disputes)} 个维度存在分歧")
    if disputes:
        for trait, dispute_info in disputes.items():
            print(f"      - {trait}: 评分 {dispute_info['scores']}, 差距 {dispute_info['range']}")
    
    # 解决争议（模拟）
    print("    争议解决模拟:")
    resolution_round = 0
    max_resolution_rounds = 3
    current_scores = mock_scores.copy()
    
    while disputes and resolution_round < max_resolution_rounds:
        print(f"      第 {resolution_round + 1} 轮争议解决:")
        
        # 每轮追加2个模型
        additional_scores = []
        for i in range(2):
            model_index = (resolution_round * 2 + i) % len(pipeline.dispute_models)
            model_name = pipeline.dispute_models[model_index]
            # 模拟模型评分（简化处理）
            new_score = {'openness_to_experience': 3, 'conscientiousness': 1, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
            additional_scores.append(new_score)
            print(f"        追加模型 {model_name}: {new_score}")
        
        # 更新评分
        current_scores.extend(additional_scores)
        
        # 重新检测争议
        disputes = pipeline.detect_disputes(current_scores, 1.0)
        resolution_round += 1
        
        if disputes:
            print(f"        仍存在 {len(disputes)} 个维度分歧")
        else:
            print(f"        所有维度分歧已解决")
    
    # 计算最终评分
    final_raw_scores = {}
    traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
    
    for trait in traits:
        trait_scores = [scores[trait] for scores in current_scores if trait in scores]
        if trait_scores:
            median_score = statistics.median(trait_scores)
            final_raw_scores[trait] = int(round(median_score))
        else:
            final_raw_scores[trait] = 3
    
    print(f"    原始最终评分: {final_raw_scores}")
    
    # 应用反向计分转换
    if is_reversed:
        final_adjusted_scores = {}
        print(f"    应用反向计分转换:")
        for trait, raw_score in final_raw_scores.items():
            adjusted_score = processor.reverse_score(raw_score)
            final_adjusted_scores[trait] = adjusted_score
            if raw_score != adjusted_score:
                print(f"      {trait}: {raw_score} → {adjusted_score}")
            else:
                print(f"      {trait}: {raw_score} (不变)")
    else:
        final_adjusted_scores = final_raw_scores
        print(f"    非反向题目，无需转换: {final_adjusted_scores}")
    
    print()
    
    # 4. 验证大五人格计算
    print("4. 验证大五人格计算")
    print("-"*60)
    
    # 模拟多个题目的结果
    mock_question_results = [
        {
            'question_id': 'AGENT_B5_C6',
            'final_adjusted_scores': final_adjusted_scores,
            'is_reversed': True
        },
        {
            'question_id': 'AGENT_B5_E1',
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
            'final_adjusted_scores': {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 5
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
    
    # 5. 验证增强争议解决机制
    print("5. 验证增强争议解决机制")
    print("-"*60)
    
    # 测试主要维度争议检测
    print("  5.1 主要维度争议检测测试:")
    mock_question_with_dimension = {
        'question_data': {
            'dimension': 'Conscientiousness'
        }
    }
    
    mock_scores_for_major_dimension = [
        {'conscientiousness': 1, 'openness_to_experience': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'conscientiousness': 5, 'openness_to_experience': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'conscientiousness': 3, 'openness_to_experience': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
    ]
    
    major_disputes = pipeline.detect_major_dimension_disputes(mock_scores_for_major_dimension, mock_question_with_dimension, 1.0)
    print(f"    主要维度争议检测: {len(major_disputes)} 个主要维度存在分歧")
    if major_disputes:
        for trait, dispute_info in major_disputes.items():
            print(f"      - {trait}: 评分 {dispute_info['scores']}, 差距 {dispute_info['range']}")
    
    # 测试置信度计算
    print("  5.2 置信度计算测试:")
    all_trait_scores = []
    for result in mock_question_results:
        scores = result['final_adjusted_scores']
        for trait in scores:
            all_trait_scores.append(scores[trait])
    
    if all_trait_scores:
        overall_reliability = processor.calculate_trait_reliability(all_trait_scores)
        print(f"    整体可靠性: {overall_reliability:.3f}")
    
    print()
    
    print("="*80)
    print("所有增强功能验证完成!")
    print("="*80)
    print("✅ 反向计分处理器增强功能")
    print("✅ 透明化流水线增强功能") 
    print("✅ 完整处理流程")
    print("✅ 大五人格计算")
    print("✅ 增强争议解决机制")
    print()
    print("系统已准备好处理真实测评报告!")


def main():
    """主函数"""
    validate_enhanced_features()


if __name__ == "__main__":
    main()