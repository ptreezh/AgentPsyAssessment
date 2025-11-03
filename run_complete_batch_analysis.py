#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的批量可信评估分析器
使用已验证的Ollama本地模型处理所有原始测评报告
"""
import sys
import os
import json
import glob
from pathlib import Path
from datetime import datetime
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from segmented_scoring_evaluator import SegmentedScoringEvaluator


def run_complete_batch_analysis(input_dir="results/readonly-original", output_dir="complete_segmented_scoring_results", max_files=None):
    """
    运行完整批量分析，使用Ollama本地模型处理所有原始测评报告
    """
    print("="*60)
    print("🚀 完整批量可信评估分析器")
    print("="*60)
    print("📋 系统配置:")
    print("   🦙 Ollama本地模型: 作为主要评估器")
    print("   ☁️  OpenRouter API: 由于API密钥失效已停用")
    print("   📁 评估方法: 5题分段独立评估")
    print("   🤖 主要模型: qwen3:4b, gemma2:2b, llama3.2:3b")
    print()
    
    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        print("请确保原始测评报告位于 results/readonly-original 目录中")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有JSON文件
    json_pattern = os.path.join(input_dir, "*.json")
    all_files = glob.glob(json_pattern)
    
    if not all_files:
        print(f"❌ 在 {input_dir} 中未找到JSON文件")
        return
    
    # 限制处理文件数量（如果指定）
    files_to_process = all_files[:max_files] if max_files else all_files
    
    print(f"📁 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print(f"📊 找到 {len(all_files)} 个原始测评报告，将处理 {len(files_to_process)} 个")
    print()
    
    # 初始化评估器（配置为优先使用Ollama模型）
    evaluator = SegmentedScoringEvaluator(use_ollama_first=True)
    
    # 统计信息
    processed_count = 0
    success_count = 0
    failed_count = 0
    total_consistency = 0
    total_reliability = 0
    passed_reliability_count = 0
    
    start_time = time.time()
    
    # 处理每个文件
    for i, file_path in enumerate(files_to_process, 1):
        filename = os.path.basename(file_path)
        print(f"📈 [{i}/{len(files_to_process)}] 处理: {filename}")
        
        try:
            # 执行评估
            result = evaluator.evaluate_file_with_multiple_models(file_path, output_dir)
            
            if result['success']:
                processed_count += 1
                success_count += 1
                
                consistency_score = result.get('consistency_score', 0)
                reliability_score = result.get('reliability_score', 0)
                reliability_passed = result.get('reliability_passed', False)
                
                total_consistency += consistency_score
                total_reliability += reliability_score
                
                if reliability_passed:
                    passed_reliability_count += 1
                
                print(f"   ✅ 一致性: {consistency_score:.2f}%")
                print(f"   ✅ 信度: {reliability_score:.2f}%")
                print(f"   ✅ 信度验证: {'通过' if reliability_passed else '未通过'}")
                print(f"   💾 结果已保存: {result['output_path']}")
            else:
                processed_count += 1
                failed_count += 1
                error_msg = result.get('error', 'Unknown error')
                print(f"   ❌ 处理失败: {error_msg}")
                
        except Exception as e:
            processed_count += 1
            failed_count += 1
            print(f"   ❌ 异常: {str(e)}")
            continue
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 打印汇总统计
    print(f"\n" + "="*60)
    print(f"📊 完整批量分析完成报告")
    print(f"⏰ 开始时间: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ 结束时间: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  总耗时: {total_time:.2f} 秒")
    print(f"📁 总文件数: {len(files_to_process)}")
    print(f"✅ 成功处理: {success_count}")
    print(f"❌ 处理失败: {failed_count}")
    print(f"🎯 成功率: {(success_count/len(files_to_process))*100:.1f}%" if len(files_to_process) > 0 else "N/A")
    
    if success_count > 0:
        avg_consistency = total_consistency / success_count
        avg_reliability = total_reliability / success_count
        
        print(f"📈 平均一致性: {avg_consistency:.2f}%")
        print(f"✅ 信度验证通过率: {passed_reliability_count}/{success_count} ({(passed_reliability_count/success_count)*100:.1f}%)")
        print(f"📈 平均信度: {avg_reliability:.2f}%")
    
    print(f"💾 结果保存在: {output_dir}")
    print("="*60)


def main():
    """
    主函数
    """
    print("可信评估分析系统 - 完整批量处理版本")
    print()
    
    # 运行完整批量分析（处理所有文件）
    run_complete_batch_analysis(max_files=None)  # 处理所有文件


if __name__ == "__main__":
    main()