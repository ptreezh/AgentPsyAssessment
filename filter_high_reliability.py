#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选高可信度评估结果
从所有已完成的评估结果中筛选出一致性高且信度通过验证的报告
"""
import sys
import os
import json
import glob
from pathlib import Path
from datetime import datetime


def filter_high_reliability_results(input_dir="segmented_scoring_results", output_dir="high_reliability_results", 
                                 min_consistency=80.0, min_reliability=0.8):
    """
    筛选高可信度评估结果
    """
    print("="*60)
    print("🔍 筛选高可信度评估结果")
    print("="*60)
    
    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有评估结果文件
    json_pattern = os.path.join(input_dir, "*_segmented_scoring_evaluation.json")
    all_files = glob.glob(json_pattern)
    
    if not all_files:
        print(f"❌ 在 {input_dir} 中未找到评估结果文件")
        return
    
    print(f"📁 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print(f"📊 找到 {len(all_files)} 个评估结果文件")
    print(f"🎯 筛选标准:")
    print(f"   最小一致性: {min_consistency}%")
    print(f"   最小信度: {min_reliability}")
    print()
    
    # 筛选结果统计
    high_reliability_count = 0
    total_consistency = 0
    total_reliability = 0
    filtered_files = []
    
    # 筛选每个文件
    for i, file_path in enumerate(all_files, 1):
        try:
            # 读取评估结果
            with open(file_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # 提取一致性分数和信度分数
            consistency_score = result_data.get('consistency_analysis', {}).get('overall_consistency', 0)
            reliability_score = result_data.get('reliability_analysis', {}).get('metrics', {}).get('overall_reliability', 0)
            reliability_passed = result_data.get('reliability_analysis', {}).get('report', {}).get('validation_passed', False)
            
            # 累积统计
            total_consistency += consistency_score
            total_reliability += reliability_score
            
            # 检查是否满足筛选标准
            if consistency_score >= min_consistency and reliability_score >= min_reliability and reliability_passed:
                high_reliability_count += 1
                filtered_files.append({
                    'file_path': file_path,
                    'consistency': consistency_score,
                    'reliability': reliability_score,
                    'filename': os.path.basename(file_path)
                })
                
                # 复制文件到高可信度目录
                output_file = os.path.join(output_dir, os.path.basename(file_path))
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ [{i}/{len(all_files)}] 高可信度: {os.path.basename(file_path)}")
                print(f"   一致性: {consistency_score:.2f}%, 信度: {reliability_score:.2f}")
            else:
                print(f"❌ [{i}/{len(all_files)}] 未达标: {os.path.basename(file_path)}")
                print(f"   一致性: {consistency_score:.2f}%, 信度: {reliability_score:.2f}")
                
        except Exception as e:
            print(f"❌ [{i}/{len(all_files)}] 处理失败: {os.path.basename(file_path)} - {str(e)}")
            continue
    
    # 计算平均值
    avg_consistency = total_consistency / len(all_files) if all_files else 0
    avg_reliability = total_reliability / len(all_files) if all_files else 0
    
    # 生成筛选报告
    filter_report = {
        "filter_date": datetime.now().isoformat(),
        "input_directory": input_dir,
        "output_directory": output_dir,
        "criteria": {
            "min_consistency": min_consistency,
            "min_reliability": min_reliability
        },
        "statistics": {
            "total_files": len(all_files),
            "high_reliability_files": high_reliability_count,
            "filter_rate": high_reliability_count / len(all_files) if all_files else 0,
            "average_consistency": avg_consistency,
            "average_reliability": avg_reliability
        },
        "high_reliability_files": filtered_files
    }
    
    # 保存筛选报告
    report_file = os.path.join(output_dir, "high_reliability_filter_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(filter_report, f, ensure_ascii=False, indent=2)
    
    # 打印最终统计
    print(f"\n" + "="*60)
    print(f"📊 高可信度筛选完成报告")
    print(f"📈 总文件数: {len(all_files)}")
    print(f"✅ 高可信度文件: {high_reliability_count}")
    print(f"🎯 筛选通过率: {(high_reliability_count/len(all_files))*100:.1f}%" if all_files else "N/A")
    print(f"📈 平均一致性: {avg_consistency:.2f}%")
    print(f"📈 平均信度: {avg_reliability:.2f}")
    print(f"💾 高可信度文件保存在: {output_dir}")
    print(f"📄 筛选报告保存在: {report_file}")
    print("="*60)
    
    return filter_report


def main():
    """
    主函数
    """
    print("高可信度评估结果筛选器")
    print()
    
    # 运行筛选
    filter_high_reliability_results()


if __name__ == "__main__":
    main()