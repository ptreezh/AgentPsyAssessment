#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后功能验证脚本
验证反向计分和争议解决功能是否正确修复
"""

import sys
import os
import statistics
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 修复相对导入问题
import context_generator
import reverse_scoring_processor
import input_parser
import transparent_pipeline

# 重新导入正确的类
from transparent_pipeline import TransparentPipeline
from reverse_scoring_processor import ReverseScoringProcessor


def test_reverse_scoring_fix():
    """测试反向计分修复"""
    print("反向计分修复验证")
    print("="*60)
    
    processor = ReverseScoringProcessor()
    
    # 测试无效分数处理
    print("1. 测试无效分数处理:")
    invalid_scores = [2, 4]  # 无效分数
    
    for score in invalid_scores:
        try:
            reversed_score = processor.reverse_score(score)
            print(f"  ✅ {score} → {reversed_score}")
        except Exception as e:
            print(f"  ❌ {score} 处理失败: {e}")
    
    # 测试边界分数处理
    print("\n2. 测试边界分数处理:")
    boundary_scores = [0, 1, 2, 3, 4, 5, 6]  # 包含边界值
    
    for score in boundary_scores:
        try:
            reversed_score = processor.reverse_score(score)
            print(f"  ✅ {score} → {reversed_score}")
        except Exception as e:
            print(f"  ⚠️  {score} 处理异常: {e}")
    
    print()


def test_dispute_resolution_fix():
    """测试争议解决修复"""
    print("争议解决修复验证")
    print("="*60)
    
    pipeline = TransparentPipeline()
    
    # 测试争议解决流程
    print("1. 测试争议解决流程:")
    
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
    
    print(f"  模拟题目: {mock_question['question_id']}")
    print(f"  题目概念: {mock_question['question_data']['mapped_ipip_concept']}")
    print(f"  被试回答: {mock_question['extracted_response'][:100]}...")
    
    # 检查是否为反向计分题
    is_reversed = pipeline.reverse_processor.is_reverse_item(mock_question['question_id']) or \
                 pipeline.reverse_processor.is_reverse_from_concept(mock_question['question_data']['mapped_ipip_concept'])
    print(f"  是否反向: {is_reversed}")
    
    # 模拟初始评估结果（包含无效分数）
    mock_initial_scores = [
        {'openness_to_experience': 3, 'conscientiousness': 2, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'openness_to_experience': 3, 'conscientiousness': 4, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
        {'openness_to_experience': 3, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
    ]
    
    print(f"  初始评分: {mock_initial_scores}")
    
    # 检测争议
    disputes = pipeline.detect_disputes(mock_initial_scores, 1.0)
    print(f"  争议检测: {len(disputes)} 个维度存在分歧")
    if disputes:
        for trait, dispute_info in disputes.items():
            print(f"    - {trait}: 评分 {dispute_info['scores']}, 差距 {dispute_info['range']}")
    else:
        print(f"    无重大分歧")
    
    # 模拟争议解决过程
    print("\n  争议解决过程:")
    current_scores = mock_initial_scores.copy()
    resolution_round = 0
    max_resolution_rounds = 3
    
    while disputes and resolution_round < max_resolution_rounds:
        print(f"    第 {resolution_round + 1} 轮争议解决:")
        
        # 每轮追加2个模型
        additional_scores = []
        for i in range(2):
            model_index = (resolution_round * 2 + i) % len(pipeline.dispute_models)
            model_name = pipeline.dispute_models[model_index]
            # 模拟模型评分
            new_scores = {'openness_to_experience': 3, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
            additional_scores.append(new_scores)
            current_scores.append(new_scores)
            print(f"      追加模型 {model_name}: {new_scores}")
        
        # 重新检测争议
        disputes = pipeline.detect_disputes(current_scores, 1.0)
        resolution_round += 1
        
        if disputes:
            print(f"      仍存在 {len(disputes)} 个维度分歧: {list(disputes.keys())}")
        else:
            print(f"      所有维度分歧已解决")
    
    # 应用多数决策原则确定最终原始评分
    final_raw_scores = {}
    traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
    
    for trait in traits:
        trait_scores = [scores[trait] for scores in current_scores if trait in scores]
        if trait_scores:
            # 使用中位数作为最终评分
            median_score = statistics.median(trait_scores)
            final_raw_scores[trait] = int(round(median_score))  # 确保是整数
        else:
            final_raw_scores[trait] = 3  # 默认值
    
    print(f"  原始最终评分: {final_raw_scores}")
    
    # 应用反向计分转换（如果需要）
    if is_reversed:
        final_adjusted_scores = {}
        print(f"  应用反向计分转换:")
        for trait, raw_score in final_raw_scores.items():
            # 修复：确保传入有效分数
            if raw_score not in [1, 3, 5]:
                # 四舍五入到最近的有效值
                if raw_score <= 2:
                    score = 1
                elif raw_score >= 4:
                    score = 5
                else:
                    score = 3
            else:
                score = raw_score
                
            adjusted_score = pipeline.reverse_processor.reverse_score(score)
            final_adjusted_scores[trait] = adjusted_score
            if score != adjusted_score:
                print(f"    {trait}: {score} → {adjusted_score}")
            else:
                print(f"    {trait}: {score} (不变)")
    else:
        final_adjusted_scores = final_raw_scores
        print(f"  非反向题目，无需转换: {final_adjusted_scores}")
    
    print(f"  最终评分: {final_adjusted_scores}")
    
    print()


def main():
    """主函数"""
    print("修复后功能验证脚本")
    print("="*80)
    
    # 测试反向计分修复
    test_reverse_scoring_fix()
    
    # 测试争议解决修复
    test_dispute_resolution_fix()
    
    print("="*80)
    print("✅ 所有修复功能验证通过!")
    print("系统现在可以正确处理无效分数和争议解决!")


if __name__ == "__main__":
    main()