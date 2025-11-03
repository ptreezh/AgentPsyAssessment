#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序 - 运行完整的单文件测评流水线
"""

import sys
import os
import json
import argparse
from pathlib import Path
from .transparent_pipeline import TransparentPipeline
from .input_parser import InputParser


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='单文件测评流水线')
    parser.add_argument('input_file', nargs='?', help='输入测评报告文件路径')
    parser.add_argument('--output-dir', default='results', help='输出目录')
    parser.add_argument('--demo', action='store_true', help='运行演示模式')
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if args.demo:
        # 运行演示模式
        run_demo_mode(output_dir)
    elif args.input_file:
        # 处理指定文件
        process_single_file(args.input_file, output_dir)
    else:
        # 交互模式
        interactive_mode(output_dir)


def run_demo_mode(output_dir):
    """运行演示模式"""
    print("运行演示模式...")
    
    # 创建演示数据
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
    
    # 创建流水线
    pipeline = TransparentPipeline()
    
    print("开始处理演示题目...")
    all_results = []
    
    for i, question in enumerate(demo_questions):
        print(f"\n{'='*60}")
        print(f"处理第 {i+1} 道题")
        print(f"{'='*60}")
        result = pipeline.process_single_question(question, i)
        all_results.append(result)
    
    # 计算最终得分
    print(f"\n{'='*60}")
    print("最终结果")
    print(f"{'='*60}")
    big5_scores = pipeline.calculate_big5_scores(all_results)
    mbti_type = pipeline.calculate_mbti_type(big5_scores)
    
    print(f"大五人格得分: {big5_scores}")
    print(f"MBTI类型: {mbti_type}")
    
    # 保存结果
    result_data = {
        'demo_mode': True,
        'big5_scores': big5_scores,
        'mbti_type': mbti_type,
        'question_count': len(demo_questions)
    }
    
    output_file = output_dir / 'demo_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")


def process_single_file(input_file, output_dir):
    """处理单个文件"""
    print(f"处理文件: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        return
    
    # 解析输入文件
    parser = InputParser()
    try:
        questions = parser.parse_assessment_json(input_file)
        print(f"解析完成，共 {len(questions)} 道题目")
    except Exception as e:
        print(f"解析文件失败: {e}")
        return
    
    # 创建流水线
    pipeline = TransparentPipeline()
    
    # 处理每道题
    print("开始处理题目...")
    all_results = []
    
    for i, question in enumerate(questions):
        print(f"\n{'='*60}")
        print(f"处理第 {i+1:02d} 道题")
        print(f"{'='*60}")
        result = pipeline.process_single_question(question, i)
        all_results.append(result)
    
    # 计算最终得分
    print(f"\n{'='*60}")
    print("最终结果")
    print(f"{'='*60}")
    big5_scores = pipeline.calculate_big5_scores(all_results)
    mbti_type = pipeline.calculate_mbti_type(big5_scores)
    
    print(f"大五人格得分: {big5_scores}")
    print(f"MBTI类型: {mbti_type}")
    
    # 保存详细结果
    result_data = {
        'input_file': input_file,
        'processed_questions': len(all_results),
        'big5_scores': big5_scores,
        'mbti_type': mbti_type,
        'question_results': all_results,
        'summary': {
            'reversed_count': sum(1 for r in all_results if r['is_reversed']),
            'disputed_count': sum(1 for r in all_results if r['resolution_rounds'] > 0)
        }
    }
    
    # 生成输出文件名
    input_path = Path(input_file)
    output_filename = f"{input_path.stem}_analysis_result.json"
    output_file = output_dir / output_filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: {output_file}")


def interactive_mode(output_dir):
    """交互模式"""
    print("单文件测评流水线 - 交互模式")
    print("="*60)
    
    # 查找可用的测评报告
    default_input_dir = Path("../results/readonly-original")
    if default_input_dir.exists():
        available_files = list(default_input_dir.glob("*.json"))
        if available_files:
            print(f"在 {default_input_dir} 中找到 {len(available_files)} 个测评报告:")
            for i, file in enumerate(available_files[:10], 1):  # 显示前10个
                print(f"  {i}. {file.name}")
            if len(available_files) > 10:
                print(f"  ... 还有 {len(available_files) - 10} 个文件")
            
            choice = input(f"\n请选择文件编号 (1-{min(10, len(available_files))}) 或输入文件路径: ")
            try:
                index = int(choice) - 1
                if 0 <= index < len(available_files):
                    selected_file = available_files[index]
                    process_single_file(str(selected_file), output_dir)
                    return
            except ValueError:
                pass
            
            # 如果输入不是数字，当作文件路径处理
            if choice and not choice.isdigit():
                process_single_file(choice, output_dir)
                return
    
    # 手动输入文件路径
    input_file = input("请输入测评报告文件路径: ").strip()
    if input_file:
        process_single_file(input_file, output_dir)
    else:
        print("未指定文件，退出程序。")


if __name__ == "__main__":
    main()