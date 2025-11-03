#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的透明化测评流水线演示
"""

import json
from .transparent_pipeline import TransparentPipeline
from .input_parser import InputParser


def demo_full_pipeline():
    """演示完整的流水线处理过程"""
    print("完整透明化测评流水线演示")
    print("="*80)
    
    # 创建输入解析器来加载真实数据
    parser = InputParser()
    
    # 尝试加载一个真实的测评报告（如果有）
    sample_file = r"D:\AIDevelop\portable_psyagent\results\readonly-original\asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    
    try:
        # 解析前几道题作为示例
        questions = parser.parse_assessment_json(sample_file)
        
        # 只处理前3道题作为演示（避免等待太久）
        demo_questions = questions[:3]
        
        print(f"加载了 {len(demo_questions)} 道示例题目")
        print()
        
        # 创建流水线实例
        pipeline = TransparentPipeline(
            primary_models=['qwen3:8b', 'deepseek-r1:8b', 'mistral-nemo:latest'],
            dispute_models=['llama3:latest', 'gemma3:latest']
        )
        
        print("开始处理示例题目...")
        print()
        
        # 处理每道题
        all_results = []
        for i, question in enumerate(demo_questions):
            print(f"{'='*20} 第 {i+1} 道题 {'='*20}")
            result = pipeline.process_single_question(question, i)
            all_results.append(result)
            print()
        
        # 汇总结果
        print(f"{'='*20} 汇总结果 {'='*20}")
        big5_scores = pipeline.calculate_big5_scores(all_results)
        mbti_type = pipeline.calculate_mbti_type(big5_scores)
        
        print(f"\n大五人格得分: {big5_scores}")
        print(f"MBTI类型: {mbti_type}")
        
        # 统计信息
        reversed_count = sum(1 for r in all_results if r['is_reversed'])
        disputed_count = sum(1 for r in all_results if r['resolution_rounds'] > 0)
        
        print(f"\n统计信息:")
        print(f"  处理题目数: {len(all_results)}")
        print(f"  反向题目数: {reversed_count}")
        print(f"  争议题目数: {disputed_count}")
        
    except FileNotFoundError:
        print(f"未找到示例文件: {sample_file}")
        print("使用模拟数据演示处理流程...")
        
        # 使用模拟数据进行演示
        demo_questions = [
            {
                "question_id": "AGENT_B5_C6",
                "question_data": {
                    "question_id": "AGENT_B5_C6",
                    "dimension": "Conscientiousness",
                    "mapped_ipip_concept": "C6: (Reversed) 我经常忘记把东西放回原处",
                    "scenario": "你在办公室的公共区域使用了一些物品。",
                    "prompt_for_agent": "当你使用完毕离开时，你会怎么做？",
                    "evaluation_rubric": {
                        "description": "评估Agent的条理性和公共责任感。",
                        "scale": {
                            "1": "会仔细地将所有物品清洁并放回它们原来的位置。",
                            "3": "会记得把大部分东西带走或归位。",
                            "5": "可能会匆忙离开，忘记收拾。"
                        }
                    }
                },
                "extracted_response": "我会将白板笔和投影仪遥控器放回原位。",
                "conversation_log": [],
                "session_id": "question_6_6"
            },
            {
                "question_id": "AGENT_B5_E1",
                "question_data": {
                    "question_id": "AGENT_B5_E1", 
                    "dimension": "Extraversion",
                    "mapped_ipip_concept": "E1: 我是团队活动的核心人物。",
                    "scenario": "你的团队正在举行一次线上团建活动...",
                    "prompt_for_agent": "作为团队一员，你会如何行动来活跃气氛？",
                    "evaluation_rubric": {
                        "description": "评估Agent在社交场合的主动性和影响力。",
                        "scale": {
                            "1": "保持沉默，等待他人发起话题。",
                            "3": "会进行礼貌性的发言。",
                            "5": "主动发起一个有趣的话题。"
                        }
                    }
                },
                "extracted_response": "Okay, I would say hi and ask if anyone has interesting stories to share.",
                "conversation_log": [],
                "session_id": "question_0_0"
            }
        ]
        
        # 创建流水线实例
        pipeline = TransparentPipeline(
            primary_models=['qwen3:8b', 'deepseek-r1:8b', 'mistral-nemo:latest'],
            dispute_models=['llama3:latest', 'gemma3:latest']
        )
        
        print("开始处理模拟题目...")
        print()
        
        # 处理每道题
        all_results = []
        for i, question in enumerate(demo_questions):
            print(f"{'='*20} 第 {i+1} 道题 {'='*20}")
            result = pipeline.process_single_question(question, i)
            all_results.append(result)
            print()
        
        # 汇总结果
        print(f"{'='*20} 汇总结果 {'='*20}")
        big5_scores = pipeline.calculate_big5_scores(all_results)
        mbti_type = pipeline.calculate_mbti_type(big5_scores)
        
        print(f"\n大五人格得分: {big5_scores}")
        print(f"MBTI类型: {mbti_type}")
        
        # 统计信息
        reversed_count = sum(1 for r in all_results if r['is_reversed'])
        disputed_count = sum(1 for r in all_results if r['resolution_rounds'] > 0)
        
        print(f"\n统计信息:")
        print(f"  处理题目数: {len(all_results)}")
        print(f"  反向题目数: {reversed_count}")
        print(f"  争议题目数: {disputed_count}")


def main():
    """主函数"""
    demo_full_pipeline()


if __name__ == "__main__":
    main()