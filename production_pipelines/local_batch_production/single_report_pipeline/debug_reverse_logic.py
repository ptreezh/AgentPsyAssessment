#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反向计分逻辑验证脚本
验证大模型评分与最终汇总的逻辑
"""

def analyze_reverse_scoring_logic():
    """分析反向计分的逻辑"""
    print("反向计分题目逻辑分析")
    print("=" * 80)
    
    print("\n反向计分题目示例: C6: (Reversed) 我经常忘记把东西放回原处")
    print("维度: 尽责性 (Conscientiousness)")
    print()
    
    print("评分标准:")
    print("  1分: 会仔细地将所有物品清洁并放回它们原来的位置，确保下一个人使用时方便整洁。")
    print("  3分: 会记得把大部分东西带走或归位，但可能会遗忘一两件小东西。") 
    print("  5分: 可能会匆忙离开，忘记收拾，将物品随意地留在原地。")
    print()
    
    print("题目概念分析:")
    print("  题目: '我经常忘记把东西放回原处'")
    print("  - 这是一个反向计分题，题目本身描述的是低尽责性行为")
    print("  - 高尽责性的人应该'不同意'这个描述")
    print("  - 低尽责性的人应该'同意'这个描述")
    print()
    
    print("大模型评估逻辑:")
    print("  - 大模型基于评分标准评估被试的回答")
    print("  - 如果回答是'我会把物品放回原位' -> 体现高尽责性行为 -> 评1分")
    print("  - 如果回答是'我会匆忙离开' -> 体现低尽责性行为 -> 评5分")
    print()
    
    print("实际意义:")
    print("  - 1分代表被试表现出了高尽责性行为（不同意题目描述）")
    print("  - 5分代表被试表现出了低尽责性行为（符合题目描述）")
    print()
    
    print("转换逻辑:")
    print("  - 但是题目概念是'我经常忘记...'，所以:")
    print("  - 被试展现高尽责性行为(1分) -> 实际上是'不同意'反向描述 -> 应记录为高尽责性(5分)")
    print("  - 被试展现低尽责性行为(5分) -> 实际上是'符合'反向描述 -> 应记录为低尽责性(1分)")
    print("  - 所以需要进行分数转换: 1→5, 5→1")
    print()
    
    print("验证示例:")
    example_response = "我会将白板笔和投影仪遥控器放回原位。"
    print(f"  被试回答: {example_response}")
    print("  - 这个回答体现了高尽责性行为")
    print("  - 按评分标准应评1分（高尽责性行为）")
    print("  - 但题目是反向的'我经常忘记...', 所以实际尽责性应为5分")
    print("  - 需要转换: 1 → 5")
    print()
    
    print("结论:")
    print("  - 大模型评分基于行为表现，是正确的")
    print("  - 但因为题目本身是反向描述，所以需要在最终汇总时进行转换")
    print("  - 这样才能得到真实的人格特质水平")


def simulate_pipeline():
    """模拟流水线的每一步"""
    print("\n" + "=" * 80)
    print("模拟流水线处理过程")
    print("=" * 80)
    
    # 模拟题目数据
    question = {
        'question_id': 'AGENT_B5_C6',
        'question_info': {
            'question_data': {
                'dimension': 'Conscientiousness',
                'mapped_ipip_concept': 'C6: (Reversed) 我经常忘记把东西放回原处',
                'evaluation_rubric': {
                    'scale': {
                        '1': '会仔细地将所有物品清洁并放回它们原来的位置，确保下一个人使用时方便整洁。',
                        '3': '会记得把大部分东西带走或归位，但可能会遗忘一两件小东西。',
                        '5': '可能会匆忙离开，忘记收拾，将物品随意地留在原地。'
                    }
                }
            }
        },
        'extracted_response': '我会将白板笔和投影仪遥控器放回原位。'
    }
    
    print(f"步骤1: 处理第{question['question_id']}题")
    print(f"  题目概念: {question['question_info']['question_data']['mapped_ipip_concept']}")
    print(f"  被试回答: {question['extracted_response']}")
    print()
    
    # 模拟三个模型的评分
    model_scores = {
        'qwen3:8b': {'conscientiousness': 1},
        'deepseek-r1:8b': {'conscientiousness': 1}, 
        'mistral-nemo:latest': {'conscientiousness': 2}  # 可能会评2分，需要转为3分
    }
    
    print("步骤2: 多模型评估结果")
    for model, scores in model_scores.items():
        trait_score = scores['conscientiousness']
        if trait_score == 2:
            trait_score = 3  # 转换为3分
        print(f"  模型 {model}: 尽责性={trait_score} (原始评分: {scores['conscientiousness']})")
    print()
    
    # 检查分歧
    original_scores = [model_scores[m]['conscientiousness'] for m in model_scores.keys()]
    converted_scores = []
    for score in original_scores:
        if score == 2:
            converted_scores.append(3)
        else:
            converted_scores.append(score)
    
    score_range = max(converted_scores) - min(converted_scores)
    print(f"步骤3: 分歧检测")
    print(f"  转换后评分: {converted_scores}")
    print(f"  评分范围: {score_range}")
    
    if score_range > 1:
        print("  发现分歧，需要争议解决")
        # 追加模型评估
        additional_scores = {'llama3:latest': {'conscientiousness': 1}}
        print(f"  追加模型 {list(additional_scores.keys())[0]} 评分: 1")
    else:
        print("  无重大分歧")
    print()
    
    # 最终评分（多数决策）
    all_converted_scores = converted_scores + [1] if score_range > 1 else converted_scores
    final_score = round(sum(all_converted_scores) / len(all_converted_scores))
    print(f"步骤4: 最终评分")
    print(f"  所有转换后评分: {all_converted_scores}")
    print(f"  平均分: {sum(all_converted_scores) / len(all_converted_scores):.1f}")
    print(f"  最终评分: {final_score}")
    print()
    
    # 反向计分转换
    is_reversed = '(Reversed)' in question['question_info']['question_data']['mapped_ipip_concept']
    if is_reversed:
        if final_score == 1:
            final_trait_score = 5
        elif final_score == 5:
            final_trait_score = 1
        else:
            final_trait_score = final_score
        print(f"步骤5: 反向计分转换")
        print(f"  题目是反向计分题: {is_reversed}")
        print(f"  转换前: {final_score} → 转换后: {final_trait_score}")
        print(f"  真实尽责性水平: {final_trait_score}")
    else:
        final_trait_score = final_score
        print(f"步骤5: 非反向计分题")
        print(f"  真实尽责性水平: {final_trait_score}")


if __name__ == "__main__":
    analyze_reverse_scoring_logic()
    simulate_pipeline()