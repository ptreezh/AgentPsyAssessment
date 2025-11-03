#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终使用示例 - 演示如何使用完整的单文件测评流水线
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .transparent_pipeline import TransparentPipeline
from .input_parser import InputParser


def demonstrate_complete_usage():
    """演示完整使用方法"""
    print("单文件测评流水线使用演示")
    print("="*60)
    
    # 方法1: 使用真实测评报告文件
    print("方法1: 处理真实测评报告文件")
    print("-"*40)
    
    # 创建流水线实例
    pipeline = TransparentPipeline()
    
    # 准备演示数据（模拟真实测评报告的一部分）
    demo_question = {
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
    
    print("处理反向计分题目示例:")
    print(f"题目ID: {demo_question['question_id']}")
    print(f"题目概念: {demo_question['question_data']['mapped_ipip_concept']}")
    print(f"被试回答: {demo_question['extracted_response']}")
    print()
    
    # 处理单道题（演示透明化过程）
    print("开始处理...")
    result = pipeline.process_single_question(demo_question, 0)
    
    print(f"\n处理完成!")
    print(f"最终评分: {result['final_adjusted_scores']}")
    print(f"是否反向: {result['is_reversed']}")
    print(f"使用模型数: {len(result['models_used'])}")
    
    # 方法2: 展示完整大五计算过程
    print("\n\n方法2: 完整大五人格计算演示")
    print("-"*40)
    
    # 模拟处理了多道题的结果
    mock_results = [
        {
            'question_id': 'AGENT_B5_C6',
            'final_adjusted_scores': {
                'openness_to_experience': 3,
                'conscientiousness': 5,  # 反向题转换后
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            },
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
                'neuroticism': 5  # 反向题转换后
            },
            'is_reversed': True
        }
    ]
    
    print("模拟处理了3道题的结果:")
    for i, res in enumerate(mock_results, 1):
        print(f"  第{i}题 ({res['question_id']}): {res['final_adjusted_scores']}")
        if res['is_reversed']:
            print(f"    注意: 这是反向计分题，分数已转换")
    
    # 计算大五得分
    print("\n计算大五人格得分:")
    big5_scores = pipeline.calculate_big5_scores(mock_results)
    print(f"大五人格得分: {big5_scores}")
    
    # 推断MBTI类型
    print("\n推断MBTI类型:")
    mbti_type = pipeline.calculate_mbti_type(big5_scores)
    print(f"MBTI类型: {mbti_type}")
    
    print("\n" + "="*60)
    print("演示完成！系统已准备好处理真实测评报告。")
    print("="*60)


def show_transparency_features():
    """展示透明化特性"""
    print("\n透明化特性展示")
    print("="*60)
    
    print("系统在处理每道题时都会提供详细反馈:")
    print()
    print("1. 处理了第几题")
    print("2. 题目概念和是否反向")
    print("3. 被试实际回答")
    print("4. 哪些模型参与了评估及评分结果")
    print("5. 是否存在分歧及如何解决")
    print("6. 最终评分和转换情况")
    print("7. MBTI推断过程")
    print("8. 统计信息汇总")
    
    print("\n示例输出片段:")
    print("""
处理第 01 题 (ID: AGENT_B5_C6)
  题目概念: C6: (Reversed) 我经常忘记把东西放回原处
  是否反向: True
  被试回答: 我会将白板笔和投影仪遥控器放回原位。...
  初始评估 (使用 3 个模型):
    └─ 使用模型 qwen3:8b 评估题目 AGENT_B5_C6...
      评分: {'openness_to_experience': 3, 'conscientiousness': 1, ...}
    └─ 使用模型 deepseek-r1:8b 评估题目 AGENT_B5_C6...
      评分: {'openness_to_experience': 3, 'conscientiousness': 1, ...}
    └─ 使用模型 mistral-nemo:latest 评估题目 AGENT_B5_C6...
      评分: {'openness_to_experience': 3, 'conscientiousness': 1, ...}
  争议检测: 0 个维度存在分歧
  原始最终评分: {'openness_to_experience': 3, 'conscientiousness': 1, ...}
  应用反向计分转换:
    openness_to_experience: 3 (不变)
    conscientiousness: 1 → 5
    extraversion: 3 (不变)
    agreeableness: 3 (不变)
    neuroticism: 3 (不变)
  最终评分: {'openness_to_experience': 3, 'conscientiousness': 5, ...}
    """)
    
    print("这种透明化设计确保了:")
    print("- 每一步处理都有明确的逻辑依据")
    print("- 评估过程可追溯、可验证")
    print("- 反向计分转换正确无误")
    print("- 最终结果可信可靠")


if __name__ == "__main__":
    demonstrate_complete_usage()
    show_transparency_features()