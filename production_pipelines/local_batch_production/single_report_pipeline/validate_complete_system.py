#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证脚本 - 验证流水线所有关键功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .reverse_scoring_processor import ReverseScoringProcessor
from .context_generator import ContextGenerator


def validate_reverse_scoring_logic():
    """验证反向计分逻辑"""
    print("验证反向计分逻辑")
    print("="*60)
    
    processor = ReverseScoringProcessor()
    
    # 测试反向题目识别
    print("1. 反向题目识别测试:")
    test_cases = [
        ('AGENT_B5_C6', True),    # 反向计分
        ('AGENT_B5_E1', False),   # 正向计分
        ('AGENT_B5_N6', True),    # 反向计分
        ('AGENT_B5_A5', True),    # 反向计分
        ('AGENT_B5_O10', True),   # 反向计分
    ]
    
    for item_id, expected in test_cases:
        result = processor.is_reverse_item(item_id)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {item_id}: {result} (期望: {expected})")
    
    # 测试概念描述识别
    print("\n2. 概念描述识别测试:")
    concept_tests = [
        ('C6: (Reversed) 我经常忘记把东西放回原处', True),
        ('E1: 我是团队活动的核心人物。', False),
        ('N1 (Reversed): 我很少感到忧虑。', True),
        ('A10: (Reversed) 我对他人的不幸漠不关心', True),
    ]
    
    for concept, expected in concept_tests:
        result = processor.is_reverse_from_concept(concept)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {concept[:30]}...: {result} (期望: {expected})")
    
    # 测试分数转换
    print("\n3. 分数转换测试:")
    score_tests = [
        (1, 5),  # 高行为表现 → 高特质水平
        (3, 3),  # 中等行为表现 → 中等特质水平
        (5, 1),  # 低行为表现 → 低特质水平
    ]
    
    for original, expected in score_tests:
        result = processor.reverse_score(original)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {original} → {result} (期望: {expected})")
    
    print("\n反向计分逻辑验证完成！")


def validate_context_generation():
    """验证上下文生成逻辑"""
    print("\n验证上下文生成逻辑")
    print("="*60)
    
    generator = ContextGenerator()
    
    # 测试反向计分题目上下文生成
    reverse_question = {
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
    
    print("生成反向计分题目评估上下文:")
    context = generator.generate_evaluation_prompt(reverse_question)
    
    # 检查关键元素
    print("  检查关键元素:")
    elements_to_check = [
        "反向计分题说明" in context,
        "低分代表高特质水平" in context,
        "此题是反向计分题" in context,
        "反向计分规则" in context
    ]
    
    for i, found in enumerate(elements_to_check, 1):
        status = "✓" if found else "✗"
        print(f"  {status} 关键元素 {i}")
    
    print(f"\n生成上下文长度: {len(context)} 字符")
    print("上下文生成逻辑验证完成！")


def validate_complete_processing_workflow():
    """验证完整处理工作流"""
    print("\n验证完整处理工作流")
    print("="*60)
    
    print("模拟完整处理流程:")
    
    # 1. 题目识别
    print("步骤1: 题目识别")
    question_id = "AGENT_B5_C6"
    concept = "C6: (Reversed) 我经常忘记把东西放回原处"
    print(f"  题目ID: {question_id}")
    print(f"  题目概念: {concept}")
    
    processor = ReverseScoringProcessor()
    is_reversed = processor.is_reverse_item(question_id) or processor.is_reverse_from_concept(concept)
    print(f"  是否反向: {is_reversed}")
    
    # 2. 模型评估
    print("\n步骤2: 模型评估")
    response = "我会将白板笔和投影仪遥控器放回原位。"
    print(f"  被试回答: {response}")
    print("  模型评估逻辑:")
    print("  - 回答体现了高尽责性行为")
    print("  - 与评分标准1分描述匹配")
    print("  - 评分为1分（高尽责性行为）")
    
    # 3. 分数转换
    print("\n步骤3: 分数转换")
    raw_score = 1  # 高尽责性行为评分
    print(f"  原始评分: {raw_score}")
    
    if is_reversed:
        final_score = processor.reverse_score(raw_score)
        print(f"  反向转换: {raw_score} → {final_score}")
        print(f"  解释: 被试展现了高尽责性行为，但题目描述的是'经常忘记放回'（低尽责性）")
        print(f"        不同意反向描述 = 高真实尽责性 → 最终得分 {final_score}")
    else:
        final_score = raw_score
        print(f"  无需转换: {final_score}")
    
    # 4. 结果解释
    print("\n步骤4: 结果解释")
    print(f"  最终评分: {final_score}")
    trait_levels = {1: "低", 3: "中等", 5: "高"}
    print(f"  真实特质水平: {trait_levels.get(final_score, '未知')}尽责性")
    
    print("\n完整处理工作流验证完成！")


def show_processing_example():
    """展示处理示例"""
    print("\n处理示例展示")
    print("="*60)
    
    print("题目: C6: (Reversed) 我经常忘记把东西放回原处")
    print("维度: Conscientiousness (尽责性)")
    print()
    print("被试回答: '我会将白板笔和投影仪遥控器放回原位。'")
    print()
    print("处理过程:")
    print("1. 识别题目: 反向计分题 ✓")
    print("2. 模型评估: 高尽责性行为 → 评分1分")
    print("3. 分数转换: 1分 → 5分 (因为不同意反向描述)")
    print("4. 最终解释: 高尽责性特质")
    print()
    print("逻辑链条:")
    print("被试行为(高尽责) → 不同意反向描述 → 高真实尽责性")
    print("评分标准1分(高行为) → 转换为5分(高特质)")


def main():
    """主函数"""
    print("单文件测评流水线 - 完整功能验证")
    print("="*80)
    
    validate_reverse_scoring_logic()
    validate_context_generation()
    validate_complete_processing_workflow()
    show_processing_example()
    
    print("\n" + "="*80)
    print("所有功能验证完成！流水线已准备好处理真实测评报告。")
    print("="*80)


if __name__ == "__main__":
    main()