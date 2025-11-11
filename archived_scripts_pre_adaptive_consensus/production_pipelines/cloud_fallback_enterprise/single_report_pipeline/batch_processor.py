#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理脚本 - 自动处理指定目录下的所有测评报告
"""

import sys
import os
import json
import argparse
from pathlib import Path
from .transparent_pipeline import TransparentPipeline
import time


def process_all_reports_in_directory(input_dir, output_dir, limit=None):
    """处理目录下的所有测评报告"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 查找所有JSON文件
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"在目录 {input_dir} 中未找到JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个测评报告文件")
    
    if limit:
        json_files = json_files[:limit]
        print(f"限制处理前 {limit} 个文件")
    
    # 创建流水线实例
    pipeline = TransparentPipeline()
    
    # 处理每个文件
    processed_count = 0
    success_count = 0
    
    for i, json_file in enumerate(json_files, 1):
        print(f"\n{'='*80}")
        print(f"处理第 {i}/{len(json_files)} 个文件: {json_file.name}")
        print(f"{'='*80}")
        
        try:
            # 处理单个文件
            result = process_single_report(pipeline, str(json_file), output_path)
            processed_count += 1
            
            if result:
                success_count += 1
                print(f"✅ 处理成功: {json_file.name}")
            else:
                print(f"❌ 处理失败: {json_file.name}")
                
        except Exception as e:
            processed_count += 1
            print(f"❌ 处理异常: {json_file.name} - {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 输出汇总统计
    print(f"\n{'='*80}")
    print("处理完成汇总")
    print(f"{'='*80}")
    print(f"总文件数: {len(json_files)}")
    print(f"已处理数: {processed_count}")
    print(f"成功处理: {success_count}")
    print(f"失败处理: {processed_count - success_count}")
    print(f"成功率: {success_count/processed_count*100:.1f}%" if processed_count > 0 else "N/A")


def process_single_report(pipeline, input_file, output_dir):
    """处理单个测评报告"""
    print(f"处理文件: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        return False
    
    # 解析输入文件
    try:
        questions = pipeline.input_parser.parse_assessment_json(input_file)
        print(f"解析完成，共 {len(questions)} 道题目")
    except Exception as e:
        print(f"解析文件失败: {e}")
        return False
    
    # 处理每道题
    print("开始处理题目...")
    all_results = []
    
    for i, question in enumerate(questions):
        print(f"\n{'-'*60}")
        print(f"处理第 {i+1:02d} 道题 ({question.get('question_id', 'Unknown')})")
        print(f"{'-'*60}")
        
        try:
            result = pipeline.process_single_question(question, i)
            all_results.append(result)
            
            # 显示进度
            if (i + 1) % 10 == 0:
                print(f"  进度: {i+1}/{len(questions)} 题已完成")
        except Exception as e:
            print(f"  ❌ 处理第 {i+1} 题时出错: {e}")
            # 继续处理下一题而不是中断
    
    # 计算最终得分
    print(f"\n{'='*60}")
    print("计算最终结果")
    print(f"{'='*60}")
    
    try:
        big5_scores = pipeline.calculate_big5_scores(all_results)
        mbti_type = pipeline.calculate_mbti_type(big5_scores)
        
        print(f"大五人格得分: {big5_scores}")
        print(f"MBTI类型: {mbti_type}")
        
        # 保存详细结果
        result_data = {
            'input_file': input_file,
            'processed_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'processed_questions': len(all_results),
            'total_questions': len(questions),
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
        input_path = Path(input_file)
        output_filename = f"{input_path.stem}_analysis_result.json"
        output_file = output_dir / output_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {output_file}")
        return True
        
    except Exception as e:
        print(f"计算最终得分时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量处理测评报告')
    parser.add_argument('--input-dir', default='../results/readonly-original', 
                       help='输入目录 (默认: ../results/readonly-original)')
    parser.add_argument('--output-dir', default='../results/single-report-results', 
                       help='输出目录 (默认: ../results/single-report-results)')
    parser.add_argument('--limit', type=int, help='限制处理文件数量')
    
    args = parser.parse_args()
    
    print("批量处理测评报告系统")
    print("="*80)
    print(f"输入目录: {args.input_dir}")
    print(f"输出目录: {args.output_dir}")
    if args.limit:
        print(f"处理限制: 最多 {args.limit} 个文件")
    print("="*80)
    
    process_all_reports_in_directory(args.input_dir, args.output_dir, args.limit)


if __name__ == "__main__":
    main()