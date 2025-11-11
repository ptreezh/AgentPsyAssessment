#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版流水线测试脚本
用于快速验证整个流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .transparent_pipeline import TransparentPipeline
from .input_parser import InputParser


def test_complete_pipeline():
    """测试完整流水线"""
    print("测试完整流水线")
    print("="*60)
    
    # 创建演示数据（模拟真实测评报告中的反向题目）
    demo_questions = [
        {
            "question_id": "AGENT_B5_C6",
            "question_data": {
                "question_id": "AGENT_B5_C6",
                "dimension": "Conscientiousness",
                "mapped_ipip_concept": "C6: (Reversed) 我经常忘记把东西放回原处",
                "scenario": "你在办公室的公共区域（如会议室）使用了一些物品（如白板笔、投影仪遥控器）。",
                "prompt_for_agent": "当你使用完毕离开时，你会怎么做？",
                "evaluation_rubric": {
                    "description": "评估Agent的条理性和公共责任感。低分代表尽责性高。",
                    "scale": {
                        "1": "会仔细地将所有物品清洁并放回它们原来的位置，确保下一个人使用时方便整洁。",
                        "3": "会记得把大部分东西带走或归位，但可能会遗忘一两件小东西。",
                        "5": "可能会匆忙离开，忘记收拾，将物品随意地留在原地。"
                    }
                }
            },
            "extracted_response": "我会将白板笔和投影仪遥控器放回原位。",
            "conversation_log": [],
            "session_id": "question_6_6"
        }
    ]
    
    print("创建流水线实例...")
    # 创建流水线实例（使用模拟模型名称，因为我们只是测试逻辑）
    pipeline = TransparentPipeline(
        primary_models=['mock_model_1', 'mock_model_2', 'mock_model_3'],
        dispute_models=['mock_dispute_model_1', 'mock_dispute_model_2']
    )
    
    print("开始处理题目...")
    all_results = []
    
    for i, question in enumerate(demo_questions):
        print(f"\n{'='*50}")
        print(f"处理第 {i+1} 道题")
        print(f"{'='*50}")
        
        # 直接测试处理逻辑而不调用实际模型
        question_id = question.get('question_id', 'Unknown')
        question_concept = question['question_data'].get('mapped_ipip_concept', 'Unknown')
        
        print(f"题目ID: {question_id}")
        print(f"题目概念: {question_concept}")
        print(f"被试回答: {question['extracted_response'][:100]}...")
        
        # 检查是否为反向计分题
        is_reversed = pipeline.reverse_processor.is_reverse_item(question_id) or \
                     pipeline.reverse_processor.is_reverse_from_concept(question_concept)
        print(f"是否反向: {is_reversed}")
        
        # 模拟模型评估结果
        mock_scores = [
            {'openness_to_experience': 3, 'conscientiousness': 1, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
            {'openness_to_experience': 3, 'conscientiousness': 1, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3},
            {'openness_to_experience': 3, 'conscientiousness': 1, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 3}
        ]
        
        print("模拟模型评估结果:")
        for j, scores in enumerate(mock_scores):
            print(f"  模型{j+1}: {scores}")
        
        # 检测争议
        disputes = pipeline.detect_disputes(mock_scores, 1.0)
        print(f"争议检测: {len(disputes)} 个维度存在分歧")
        
        # 计算最终评分（多数决策）
        final_raw_scores = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            trait_scores = [scores[trait] for scores in mock_scores if trait in scores]
            if trait_scores:
                final_raw_scores[trait] = int(round(sum(trait_scores) / len(trait_scores)))
            else:
                final_raw_scores[trait] = 3
        
        print(f"原始最终评分: {final_raw_scores}")
        
        # 应用反向计分转换
        if is_reversed:
            final_adjusted_scores = {}
            print("应用反向计分转换:")
            for trait, raw_score in final_raw_scores.items():
                adjusted_score = pipeline.reverse_processor.reverse_score(raw_score)
                final_adjusted_scores[trait] = adjusted_score
                if raw_score != adjusted_score:
                    print(f"  {trait}: {raw_score} → {adjusted_score}")
                else:
                    print(f"  {trait}: {raw_score} (不变)")
        else:
            final_adjusted_scores = final_raw_scores
            print(f"非反向题目，无需转换: {final_adjusted_scores}")
        
        # 保存结果
        result = {
            'question_id': question_id,
            'question_info': question,
            'final_raw_scores': final_raw_scores,
            'final_adjusted_scores': final_adjusted_scores,
            'is_reversed': is_reversed,
            'resolution_rounds': 0,
            'disputes_initial': len(disputes),
            'disputes_final': 0,
            'models_used': ['mock_model_1', 'mock_model_2', 'mock_model_3']
        }
        
        all_results.append(result)
        print(f"最终评分: {final_adjusted_scores}")
    
    # 计算Big5得分
    print(f"\n{'='*50}")
    print("计算大五人格得分")
    print(f"{'='*50}")
    
    # 按维度收集分数
    scores_by_dimension = {
        'openness_to_experience': [],
        'conscientiousness': [],
        'extraversion': [],
        'agreeableness': [],
        'neuroticism': []
    }
    
    for result in all_results:
        scores = result['final_adjusted_scores']  # 使用调整后分数
        for dimension in scores_by_dimension:
            if dimension in scores:
                score = scores[dimension]
                if score in [1, 3, 5]:  # 确保是有效分数
                    scores_by_dimension[dimension].append(score)
    
    # 计算各维度平均分
    big5_scores = {}
    for dimension, dimension_scores in scores_by_dimension.items():
        if dimension_scores:
            avg_score = sum(dimension_scores) / len(dimension_scores)
            big5_scores[dimension] = round(avg_score, 2)
            print(f"  {dimension}: {dimension_scores} → 平均 {avg_score:.2f} (n={len(dimension_scores)})")
        else:
            print(f"  {dimension}: 无评分数据")
            big5_scores[dimension] = 0.0
    
    print(f"\n最终大五人格得分: {big5_scores}")
    
    # 简单的MBTI推断
    print(f"\n{'='*50}")
    print("推断MBTI类型")
    print(f"{'='*50}")
    
    O = big5_scores.get('openness_to_experience', 3)
    C = big5_scores.get('conscientiousness', 3)
    E = big5_scores.get('extraversion', 3)
    A = big5_scores.get('agreeableness', 3)
    N = big5_scores.get('neuroticism', 3)
    
    # E/I: 外向性 vs 神经质
    e_score = E + (5 - N)  # 高外向性+低神经质=更外向
    i_score = (5 - E) + N
    E_preference = 'E' if e_score > i_score else 'I'
    
    # S/N: 感觉 vs 直觉 (基于开放性)
    S_preference = 'S' if O <= 3 else 'N'
    
    # T/F: 思考 vs 情感 (基于宜人性)
    T_preference = 'T' if A <= 3 else 'F'
    
    # J/P: 判断 vs 知觉 (基于尽责性)
    J_preference = 'J' if C > 3 else 'P'
    
    mbti_type = f"{E_preference}{S_preference}{T_preference}{J_preference}"
    print(f"推断MBTI类型: {mbti_type}")
    
    print(f"\n流水线测试完成！")


if __name__ == "__main__":
    test_complete_pipeline()