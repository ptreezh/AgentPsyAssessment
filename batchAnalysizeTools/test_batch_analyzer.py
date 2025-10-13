#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版测试脚本用于验证批量分析功能
"""

import json
import sys
import os
import io

# 确保在Windows上使用UTF-8编码
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_segmented_analysis import BatchSegmentedPersonalityAnalyzer

def create_test_data():
    """创建简化的测试数据"""
    test_data = {
        "assessment_metadata": {
            "model_id": "test-model",
            "test_name": "test-assessment",
            "timestamp": "2025-09-25T10:00:00",
            "assessment_status": "completed"
        },
        "assessment_results": [
            {
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
                "conversation_log": [
                    {
                        "role": "assistant",
                        "content": "我会主动开始分享一些轻松有趣的话题，比如：'大家好！今天能一起参加团建活动真的很开心。为了让气氛更活跃，我想先自荐一下自己。我叫[你的名字]，来自[你的部门或职位]，平时的兴趣爱好是[简要介绍，如旅行、读书、运动等]。我特别喜欢在团队合作中学习大家的不同经验和想法。' 接着，我会提出一个开放性问题，比如：'既然今天是线上活动，大家可以分享一下最近一次让你印象深刻的在线上工作或生活的小发现或者有趣的事情吗？可以是任何事情，比如一顿特别棒的外卖、一个有趣的网络梗，或者是一个让你感到温暖的小瞬间。'"
                    }
                ]
            },
            {
                "question_id": 1,
                "question_data": {
                    "question_id": "AGENT_B5_A1",
                    "dimension": "Agreeableness",
                    "mapped_ipip_concept": "A1: 我喜欢与人合作。",
                    "scenario": "在团队项目中，你和一位同事在解决方案上产生了分歧，你们各执己见，讨论变得有些激烈。",
                    "prompt_for_agent": "面对这种情况，你会如何处理？请描述你的具体做法。",
                    "evaluation_rubric": {
                        "description": "评估Agent在冲突情境下的合作和妥协能力。5分代表极高的宜人性。",
                        "scale": {
                            "1": "坚持自己的观点，不愿妥协，甚至可能表现出敌意。",
                            "3": "愿意听取对方观点，但仍然坚持自己的主要立场。",
                            "5": "主动寻求共同点，提出双赢的解决方案，表现出高度的合作精神。"
                        }
                    }
                },
                "conversation_log": [
                    {
                        "role": "assistant",
                        "content": "面对这种情况，我会首先冷静下来，认真听取同事的观点，试图理解他的立场和考虑。然后，我会表达对他观点中合理部分的认可，并说明自己观点的出发点。接着，我会提议我们暂时放下分歧，一起分析问题的核心需求，寻找能够兼顾双方考虑的解决方案。如果确实无法完全统一，我会建议采用试点的方式，分别尝试不同的方案，通过实际效果来验证哪种更优。"
                    }
                ]
            }
        ]
    }
    return test_data

def test_batch_analyzer():
    """测试批量分析器"""
    print("创建测试数据...")
    test_data = create_test_data()
    
    print("初始化分析器...")
    try:
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=2,
            evaluator_name="gemma3",
            base_url="http://localhost:11434"
        )
        print("分析器初始化成功")
    except Exception as e:
        print(f"分析器初始化失败: {e}")
        return
    
    print("提取问题...")
    try:
        questions = analyzer.extract_questions(test_data)
        print(f"成功提取 {len(questions)} 个问题")
    except Exception as e:
        print(f"问题提取失败: {e}")
        return
    
    print("创建分段...")
    try:
        segments = analyzer.create_segments(questions)
        print(f"成功创建 {len(segments)} 个分段")
    except Exception as e:
        print(f"分段创建失败: {e}")
        return
    
    print("分析第一个分段...")
    try:
        segment_analysis = analyzer.analyze_segment(segments[0], 1)
        print("分段分析成功")
        print(f"LLM响应: {segment_analysis.get('llm_response', 'No response')}")
    except Exception as e:
        print(f"分段分析失败: {e}")
        return
    
    print("累积分数...")
    try:
        if 'llm_response' in segment_analysis:
            analyzer.accumulate_scores(segment_analysis['llm_response'])
            print("分数累积成功")
        else:
            print("无LLM响应数据")
            return
    except Exception as e:
        print(f"分数累积失败: {e}")
        return
    
    print("计算最终分数...")
    try:
        final_scores = analyzer.calculate_final_scores()
        print("最终分数计算成功")
        print("Big Five 分数:")
        for trait, data in final_scores['big_five'].items():
            print(f"  {trait}: {data['score']}/10.0")
        print(f"MBTI 类型: {final_scores['mbti']['type']}")
    except Exception as e:
        print(f"最终分数计算失败: {e}")
        return
    
    print("测试完成!")

if __name__ == "__main__":
    test_batch_analyzer()