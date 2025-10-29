#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理results\results目录下的测评报告，进行五题分段分析
使用本地Ollama模型进行评估，改进JSON解析能力
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import glob

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from segmented_analysis import SegmentedPersonalityAnalyzer
# from enhanced_ollama_evaluator import EnhancedOllamaEvaluator  # 模块不存在，暂时注释掉

def get_result_files(results_dir: str = "results/results") -> List[str]:
    """获取所有测评报告文件"""
    pattern = os.path.join(results_dir, "*.json")
    files = glob.glob(pattern)
    
    # 排除已经分析过的文件
    filtered_files = []
    for file in files:
        if not file.endswith("_segmented_analysis.json"):
            filtered_files.append(file)
    
    print(f"找到 {len(filtered_files)} 个测评报告文件")
    return sorted(filtered_files)

def analyze_single_file(file_path: str, evaluator_name: str = "phi3_mini") -> bool:
    """分析单个文件"""
    print(f"\n=== 开始分析: {file_path} ===")
    
    try:
        # 检查是否已存在分析结果
        output_file = file_path.replace(".json", "_segmented_analysis.json")
        if os.path.exists(output_file):
            print(f"  跳过，分析结果已存在: {output_file}")
            return True
            
        # 初始化分析器
        analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=5, evaluator_name=evaluator_name)
        
        # 加载测评数据
        assessment_data = None
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    assessment_data = json.load(f)
                print(f"  使用 {encoding} 编码读取文件成功")
                break
            except UnicodeDecodeError:
                continue
            except json.JSONDecodeError as e:
                print(f"  使用 {encoding} 编码读取文件成功但JSON解析失败: {e}")
                continue
        
        if assessment_data is None:
            print(f"  错误: 无法读取文件 {file_path}")
            return False
            
        # 提取问题
        questions = analyzer.extract_questions(assessment_data)
        print(f"  总问题数: {len(questions)}")
        
        if len(questions) == 0:
            print(f"  警告: 文件 {file_path} 中没有有效问题")
            return False
            
        # 创建分段
        segments = analyzer.create_segments(questions)
        print(f"  分段数: {len(segments)}")
        
        # 分析每个段
        for i, segment in enumerate(segments):
            print(f"  分析段 {i+1}/{len(segments)}: {len(segment)} 个问题")
            dimensions = list(set(q.get('dimension', 'Unknown') for q in segment))
            print(f"    涵盖维度: {dimensions}")
            
            try:
                segment_analysis = analyzer.analyze_segment(segment, i+1)
                
                if 'llm_response' in segment_analysis:
                    analyzer.accumulate_scores(segment_analysis['llm_response'])
                    print(f"    段 {i+1} 分析完成并累积分数")
                else:
                    print(f"    警告: 段 {i+1} 缺少分析结果")
                    return False
                    
            except Exception as e:
                print(f"    段 {i+1} 分析失败: {e}")
                print("    由于模型调用失败，跳过此文件")
                return False
                
        # 计算最终分数
        final_scores = analyzer.calculate_final_scores()
        
        # 输出结果
        print(f"\n  === {Path(file_path).name} 分析结果 ===")
        print("  Big Five 分数:")
        for trait, data in final_scores['big_five'].items():
            print(f"    {trait}: {data['score']}/10.0 (基于 {data['weight']} 个问题)")
        
        print(f"\n  MBTI 类型: {final_scores['mbti']['type']} (置信度: {final_scores['mbti']['confidence']})")
        print(f"  A/T 类型: {final_scores['at_type']['type']} (神经质分数: {final_scores['at_type']['neuroticism_score']})")
        
        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_scores, f, ensure_ascii=False, indent=2)
        print(f"\n  结果已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"  分析文件 {file_path} 时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def batch_analyze_results(results_dir: str = "results/results", 
                         evaluator_name: str = "phi3_mini",
                         max_files: int = None) -> Dict[str, Any]:
    """批量分析测评报告"""
    
    print("=== 开始批量五题分段分析 ===")
    print(f"评估器: {evaluator_name}")
    print(f"目标目录: {results_dir}")
    
    # 获取文件列表
    files = get_result_files(results_dir)
    
    if max_files:
        files = files[:max_files]
        print(f"限制分析前 {max_files} 个文件")
    
    if not files:
        print("未找到可分析的测评报告文件")
        return {"success": 0, "failed": 0, "total": 0}
    
    print(f"\n将分析 {len(files)} 个文件:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {Path(file).name}")
    
    # 批量分析
    success_count = 0
    failed_files = []
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] " + "="*50)
        
        if analyze_single_file(file_path, evaluator_name):
            success_count += 1
        else:
            failed_files.append(file_path)
            
        # 添加延时，避免过度请求
        import time
        time.sleep(1)
    
    # 生成汇总报告
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(files),
        "success_count": success_count,
        "failed_count": len(failed_files),
        "success_rate": success_count / len(files) if len(files) > 0 else 0,
        "failed_files": failed_files,
        "evaluator_used": evaluator_name,
        "segment_size": 5
    }
    
    # 保存汇总报告
    summary_file = os.path.join(results_dir, f"batch_5segment_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 批量分析完成 ===")
    print(f"成功分析: {success_count}/{len(files)} 个文件")
    print(f"失败文件: {len(failed_files)} 个")
    print(f"成功率: {summary['success_rate']:.1%}")
    print(f"汇总报告: {summary_file}")
    
    if failed_files:
        print(f"\n失败的文件列表:")
        for file in failed_files:
            print(f"  - {file}")
    
    return summary

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量五题分段分析测评报告')
    parser.add_argument('--results_dir', default='results/results', help='测评报告目录路径')
    parser.add_argument('--evaluator', default='glm_4_6_cloud', 
                       choices=['glm_4_6_cloud', 'deepseek_v3_1_cloud', 'qwen3_vl_cloud', 'gpt_oss_120b_cloud', 'phi3_mini', 'qwen3_4b', 'ollama_mistral'],
                       help='使用的评估器名称')
    parser.add_argument('--max_files', type=int, help='最大分析文件数量（用于测试）')
    
    args = parser.parse_args()
    
    summary = batch_analyze_results(
        results_dir=args.results_dir,
        evaluator_name=args.evaluator,
        max_files=args.max_files
    )

if __name__ == "__main__":
    main()