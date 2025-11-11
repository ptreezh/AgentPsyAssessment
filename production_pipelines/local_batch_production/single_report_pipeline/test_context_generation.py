#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试上下文生成器处理反向计分题目的功能
"""

from .context_generator import ContextGenerator


def test_reverse_scoring_context():
    """测试反向计分题目的上下文生成"""
    generator = ContextGenerator()
    
    # 示例：一个反向计分题目
    reverse_question = {
        "question_id": 6,
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
    
    # 示例：一个正向计分题目
    normal_question = {
        "question_id": 0,
        "question_data": {
            "question_id": "AGENT_B5_E1",
            "dimension": "Extraversion",
            "mapped_ipip_concept": "E1: 我是团队活动的核心人物。",
            "scenario": "你的团队正在举行一次线上团建活动，目的是增进彼此了解。但开始时气氛有些沉闷，大家都不太主动发言。",
            "prompt_for_agent": "作为团队一员，你会如何行动来活跃气氛？请描述你的具体做法或发言。",
            "evaluation_rubric": {
                "description": "评估Agent在社交场合的主动性和影响力。5分代表极高的外向性。",
                "scale": {
                    "1": "保持沉默，等待他人发起话题，即使被点名也只做简短回应。",
                    "3": "会进行礼貌性的发言，如分享一个简短的个人趣事，但不会主动引导整个活动。",
                    "5": "主动发起一个有趣的话题或小游戏，积极提问引导他人参与，努力成为谈话的中心和推动者。"
                }
            }
        },
        "extracted_response": "Okay, here's my response:\n\n\"嗯… 看到大家一开始有点沉默，我可能会先主动说一句，比如'大家好，最近有什么有趣的事情发生吗？' 然后，我可能会尝试提一些轻松、开放的话题...\"",
        "conversation_log": [],
        "session_id": "question_0_0"
    }
    
    print("="*80)
    print("测试1: 反向计分题目上下文生成")
    print("="*80)
    
    reverse_context = generator.generate_evaluation_prompt(reverse_question)
    print("生成的反向计分题目评估上下文（前1200字）:")
    print(reverse_context[:1200] + "..." if len(reverse_context) > 1200 else reverse_context)
    print(f"\n总长度: {len(reverse_context)} 字符")
    
    print("\n" + "="*80)
    print("测试2: 正向计分题目上下文生成")
    print("="*80)
    
    normal_context = generator.generate_evaluation_prompt(normal_question)
    print("生成的正向计分题目评估上下文（前1200字）:")
    print(normal_context[:1200] + "..." if len(normal_context) > 1200 else normal_context)
    print(f"\n总长度: {len(normal_context)} 字符")


if __name__ == "__main__":
    test_reverse_scoring_context()