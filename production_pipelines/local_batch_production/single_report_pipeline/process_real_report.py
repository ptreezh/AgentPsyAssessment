#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的真实测评报告处理脚本
专门用于处理单个真实的测评报告
"""

import sys
import os
import json
from pathlib import Path
from .transparent_pipeline import TransparentPipeline


def process_real_assessment_report(file_path):
    """处理真实的测评报告"""
    print(f"处理真实的测评报告: {file_path}")
    print("="*80)
    
    if not os.path.exists(file_path):
        print(f"❌ 错误: 文件不存在: {file_path}")
        return None
    
    # 创建流水线实例
    pipeline = TransparentPipeline()
    
    # 解析输入文件
    print("1. 解析输入文件...")
    try:
        questions = pipeline.input_parser.parse_assessment_json(file_path)
        print(f"   ✅ 解析完成，共 {len(questions)} 道题目")
    except Exception as e:
        print(f"   ❌ 解析文件失败: {e}")
        return None
    
    # 处理每道题
    print("\n2. 逐题处理与评估...")
    print("-" * 80)
    
    all_results = []
    for i, question in enumerate(questions):
        print(f"\n第 {i+1:02d} 道题 (ID: {question.get('question_id', 'Unknown')})")
        print("-" * 60)
        
        try:
            result = pipeline.process_single_question(question, i)
            all_results.append(result)
            
            # 显示关键信息
            concept = question['question_data'].get('mapped_ipip_concept', 'Unknown')
            is_reversed = result.get('is_reversed', False)
            final_scores = result.get('final_adjusted_scores', {})
            
            print(f"  题目概念: {concept}")
            print(f"  是否反向: {is_reversed}")
            print(f"  最终评分: {final_scores}")
            print(f"  争议解决: {result.get('resolution_rounds', 0)} 轮")
            
        except Exception as e:
            print(f"  ❌ 处理第 {i+1} 题时出错: {e}")
            continue
    
    # 计算最终得分
    print(f"\n3. 计算最终大五人格得分...")
    print("-" * 80)
    
    try:
        big5_scores = pipeline.calculate_big5_scores(all_results)
        mbti_type = pipeline.calculate_mbti_type(big5_scores)
        
        print("大五人格得分:")
        for dimension, score in big5_scores.items():
            print(f"  {dimension}: {score}")
        
        print(f"\nMBTI类型: {mbti_type}")
        
        # 保存结果
        result_data = {
            'input_file': file_path,
            'processed_questions': len(all_results),
            'big5_scores': big5_scores,
            'mbti_type': mbti_type,
            'question_results': all_results,
            'summary': {
                'reversed_count': sum(1 for r in all_results if r['is_reversed']),
                'disputed_count': sum(1 for r in all_results if r['resolution_rounds'] > 0),
                'models_called': sum(len(r['models_used']) for r in all_results)
            }
        }
        
        # 生成输出文件名
        input_path = Path(file_path)
        output_dir = Path("../results/single-report-results")
        output_dir.mkdir(exist_ok=True)
        output_filename = f"{input_path.stem}_analysis_result.json"
        output_file = output_dir / output_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 结果已保存到: {output_file}")
        return result_data
        
    except Exception as e:
        print(f"   ❌ 计算最终得分时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='处理真实的测评报告')
    parser.add_argument('file_path', nargs='?', 
                       help='测评报告文件路径')
    parser.add_argument('--default', action='store_true',
                       help='使用默认文件路径')
    
    args = parser.parse_args()
    
    # 默认处理的测评报告文件
    default_file = r"..\results\readonly-original\asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    
    print("单文件测评流水线 - 真实测评报告处理")
    print("="*80)
    
    # 确定要处理的文件
    if args.file_path:
        file_path = args.file_path
        print(f"使用指定文件: {file_path}")
    elif args.default:
        file_path = default_file
        print(f"使用默认文件: {file_path}")
    else:
        # 交互式选择
        if os.path.exists(default_file):
            print(f"找到默认测评报告: {default_file}")
            choice = input("是否使用默认文件? (y/n) 或输入其他文件路径: ").strip()
            if choice.lower() in ['y', 'yes', '']:
                file_path = default_file
            else:
                file_path = choice
        else:
            print("未找到默认文件")
            file_path = input("请输入测评报告文件路径: ").strip()
    
    if not file_path:
        print("未提供文件路径，退出程序。")
        return
    
    if not os.path.exists(file_path):
        print(f"❌ 错误: 文件不存在: {file_path}")
        return
    
    # 处理文件
    result = process_real_assessment_report(file_path)
    
    if result:
        print(f"\n{'='*80}")
        print("处理完成!")
        print(f"{'='*80}")
        print(f"处理题目数: {result['processed_questions']}")
        print(f"大五人格得分: {result['big5_scores']}")
        print(f"MBTI类型: {result['mbti_type']}")
        print(f"反向题目数: {result['summary']['reversed_count']}")
        print(f"争议解决数: {result['summary']['disputed_count']}")
        print(f"模型调用数: {result['summary']['models_called']}")
    else:
        print("处理失败!")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()