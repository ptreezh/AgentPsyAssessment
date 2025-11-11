#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的增强争议解决流水线演示
展示从争议检测到解决再到置信度验证的完整流程
"""

import sys
import os
import statistics
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .transparent_pipeline import TransparentPipeline
from .reverse_scoring_processor import ReverseScoringProcessor


def demonstrate_complete_enhanced_pipeline():
    """演示完整的增强争议解决流水线"""
    print("完整的增强争议解决流水线演示")
    print("="*80)
    
    # 创建流水线实例
    pipeline = TransparentPipeline()
    processor = ReverseScoringProcessor()
    
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
        'extracted_response': '我会将白板笔和投影仪遥控器放回原位。',
        'conversation_log': [],
        'session_id': 'question_6_6'
    }
    
    print("模拟题目:")
    print(f"  ID: {mock_question['question_id']}")
    print(f"  概念: {mock_question['question_data']['mapped_ipip_concept']}")
    print(f"  回答: {mock_question['extracted_response']}")
    print()
    
    # 模拟三个初始评估模型的评分（存在分歧）
    mock_initial_scores = [
        {
            'model': 'qwen3:8b',
            'scores': {
                'openness_to_experience': 3,
                'conscientiousness': 1,  # 高尽责性
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
        },
        {
            'model': 'deepseek-r1:8b',
            'scores': {
                'openness_to_experience': 3,
                'conscientiousness': 3,  # 中等尽责性
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
        },
        {
            'model': 'mistral-nemo:latest',
            'scores': {
                'openness_to_experience': 3,
                'conscientiousness': 5,  # 低尽责性（分歧）
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
        }
    ]
    
    print("初始评估结果 (3个模型):")
    for i, score_data in enumerate(mock_initial_scores, 1):
        model = score_data['model']
        scores = score_data['scores']
        print(f"  模型{i} ({model}): {scores}")
    
    # 提取尽责性维度的评分
    conscientiousness_scores = [s['scores']['conscientiousness'] for s in mock_initial_scores]
    print(f"\n尽责性维度评分: {conscientiousness_scores}")
    
    # 计算初始信度和争议严重程度
    initial_reliability = processor.calculate_trait_reliability(conscientiousness_scores)
    initial_severity = processor.assess_dispute_severity(conscientiousness_scores)
    print(f"初始信度: {initial_reliability:.3f}")
    print(f"争议严重程度: {initial_severity}")
    
    # 检测争议
    disputes = pipeline.detect_major_dimension_disputes(
        [s['scores'] for s in mock_initial_scores], 
        mock_question, 
        1.0
    )
    
    print(f"\n争议检测结果:")
    if disputes:
        for trait, dispute_info in disputes.items():
            print(f"  {trait}: 评分 {dispute_info['scores']}")
            print(f"    范围: {dispute_info['range']}")
            print(f"    信度: {dispute_info['reliability']:.3f}")
            print(f"    严重程度: {dispute_info['severity']}")
    else:
        print("  无重大争议")
    
    # 模拟争议解决过程（追加2个模型）
    print(f"\n开始争议解决过程...")
    all_scores = [s['scores'] for s in mock_initial_scores]
    
    # 第1轮争议解决（追加2个模型）
    print("第1轮争议解决:")
    additional_scores_round1 = [
        {
            'model': 'llama3:latest',
            'scores': {
                'openness_to_experience': 3,
                'conscientiousness': 1,  # 高尽责性
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
        },
        {
            'model': 'gemma3:latest',
            'scores': {
                'openness_to_experience': 3,
                'conscientiousness': 1,  # 高尽责性
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
        }
    ]
    
    print("  追加模型:")
    for score_data in additional_scores_round1:
        model = score_data['model']
        scores = score_data['scores']
        all_scores.append(scores)
        print(f"    {model}: {scores}")
    
    # 更新尽责性维度的评分
    updated_conscientiousness_scores = [s['conscientiousness'] for s in all_scores]
    print(f"  更新后尽责性评分: {updated_conscientiousness_scores}")
    
    # 计算更新后的信度
    updated_reliability = processor.calculate_trait_reliability(updated_conscientiousness_scores)
    updated_severity = processor.assess_dispute_severity(updated_conscientiousness_scores)
    print(f"  更新后信度: {updated_reliability:.3f}")
    print(f"  更新后争议严重程度: {updated_severity}")
    
    # 重新检测争议
    updated_disputes = pipeline.detect_major_dimension_disputes(all_scores, mock_question, 1.0)
    print(f"  重新检测争议:")
    if updated_disputes:
        for trait, dispute_info in updated_disputes.items():
            print(f"    {trait}: 评分 {dispute_info['scores']}")
            print(f"      范围: {dispute_info['range']}")
            print(f"      信度: {dispute_info['reliability']:.3f}")
            print(f"      严重程度: {dispute_info['severity']}")
    else:
        print("    无重大争议")
    
    # 应用多数决策原则确定最终评分
    final_raw_score = int(round(sum(updated_conscientiousness_scores) / len(updated_conscientiousness_scores)))
    final_median_score = int(statistics.median(updated_conscientiousness_scores))
    
    print(f"\n最终评分确定:")
    print(f"  平均分: {sum(updated_conscientiousness_scores) / len(updated_conscientiousness_scores):.2f}")
    print(f"  中位数: {statistics.median(updated_conscientiousness_scores):.2f}")
    print(f"  最终原始评分: {final_raw_score}")
    
    # 应用反向计分转换（因为是反向题目）
    is_reversed = processor.is_reverse_item(mock_question['question_id']) or \
                 processor.is_reverse_from_concept(mock_question['question_data']['mapped_ipip_concept'])
    
    if is_reversed:
        final_adjusted_score = processor.reverse_score(final_raw_score)
        print(f"  应用反向计分转换: {final_raw_score} → {final_adjusted_score}")
        print(f"  最终调整后评分: {final_adjusted_score} (高尽责性)")
    else:
        final_adjusted_score = final_raw_score
        print(f"  非反向题目，最终评分: {final_adjusted_score}")
    
    # 验证解决结果置信度
    original_scores_for_validation = [1, 3, 5]  # 初始分歧评分
    resolved_scores_for_validation = [1, 1, 1, 1, 1]  # 解决后一致评分
    
    confidence_result = processor.validate_resolution_confidence(
        original_scores_for_validation, 
        resolved_scores_for_validation
    )
    
    print(f"\n置信度验证:")
    print(f"  原始评分: {original_scores_for_validation}")
    print(f"  解决后评分: {resolved_scores_for_validation}")
    print(f"  置信度评估: {confidence_result}")
    
    # 最终总结
    print(f"\n{'='*80}")
    print("争议解决流水线总结")
    print(f"{'='*80}")
    print(f"题目ID: {mock_question['question_id']}")
    print(f"题目概念: {mock_question['question_data']['mapped_ipip_concept']}")
    print(f"是否反向: {is_reversed}")
    print(f"初始评分分歧: {conscientiousness_scores}")
    print(f"初始信度: {initial_reliability:.3f}")
    print(f"争议严重程度: {initial_severity}")
    print(f"争议解决轮次: 1轮 (追加2个模型)")
    print(f"最终评分: {final_adjusted_score}")
    print(f"最终信度: {updated_reliability:.3f}")
    print(f"置信度: {confidence_result['confidence']:.2f}")
    print(f"可靠性提升: {confidence_result['reliability_gain']:.3f}")
    
    print(f"\n流水线优势:")
    print(f"  1. 多模型评估确保评分全面性")
    print(f"  2. 信度计算量化评估质量")
    print(f"  3. 分层争议解决提高准确性")
    print(f"  4. 置信度验证确保结果可信")
    print(f"  5. 反向计分正确处理确保人格特质准确性")


def main():
    """主函数"""
    demonstrate_complete_enhanced_pipeline()


if __name__ == "__main__":
    main()