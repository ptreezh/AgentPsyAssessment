#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实测评报告批量分析脚本
处理实际的测评报告文件，支持断点续跑
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_report_analyzer import BatchReportAnalyzer


def process_real_assessment_reports():
    """处理真实的测评报告"""
    print("真实测评报告批量分析")
    print("="*80)
    
    # 设置输入输出目录
    input_dir = Path(r"D:\AIDevelop\portable_psyagent\results\readonly-original")
    output_dir = Path(r"D:\AIDevelop\portable_psyagent\results\real-batch-analysis-results")
    
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 检查输入目录
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return False
    
    # 创建批量分析器
    analyzer = BatchReportAnalyzer(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        checkpoint_interval=5  # 每5个文件保存一次检查点
    )
    
    # 查找测评报告文件
    print("📂 查找测评报告文件...")
    json_files = analyzer.find_json_files("*.json")
    
    if not json_files:
        print("❌ 未找到任何测评报告文件")
        return False
    
    print(f"  找到 {len(json_files)} 个测评报告文件")
    print(f"  已处理: {len(analyzer.processed_files)} 个")
    print(f"  剩余: {len(json_files) - len(analyzer.processed_files)} 个")
    print()
    
    # 确定起始位置
    start_index = 0
    if analyzer.current_file_index < len(json_files):
        start_index = analyzer.current_file_index
    
    print(f"▶️  从第 {start_index + 1} 个文件开始处理")
    print()
    
    # 处理文件
    processed_count = 0
    success_count = 0
    failed_count = 0
    
    # 限制处理文件数量用于演示
    limit = min(10, len(json_files))  # 最多处理10个文件
    
    for i, file_path in enumerate(json_files[start_index:start_index+limit], start_index):
        # 检查是否已处理过
        if str(file_path) in analyzer.processed_files:
            print(f"⏭️  跳过已处理文件: {file_path.name}")
            continue
        
        # 处理文件
        print(f"🔍 处理第 {i+1:02d} 个文件: {file_path.name}")
        result = analyzer.process_single_report(file_path)  # 传递Path对象而不是字符串
        
        # 更新状态
        analyzer.processed_files.add(str(file_path))
        analyzer.results.append(result)
        analyzer.current_file_index = i + 1
        
        if result.get('success', False):
            success_count += 1
            print(f"  ✅ 完成: {file_path.name}")
            print(f"    大五人格: {result.get('big5_scores', {})}")
            print(f"    MBTI类型: {result.get('mbti_type', 'Unknown')}")
        else:
            failed_count += 1
            print(f"  ❌ 失败: {file_path.name}")
            error_msg = result.get('error', 'Unknown error') if result else 'No result'
            print(f"    错误: {error_msg}")
        
        processed_count += 1
        
        # 显示进度
        if processed_count % 5 == 0:
            print(f"  📊 进度: {processed_count} 个文件已处理 "
                  f"(成功: {success_count}, 失败: {failed_count})")
        
        # 保存检查点
        if processed_count % analyzer.checkpoint_interval == 0:
            print(f"  💾 保存检查点...")
            analyzer.save_checkpoint()
            analyzer.save_results()
            analyzer.save_summary_report()
        
        # 添加延迟避免API过载
        time.sleep(1)
    
    # 保存最终结果
    print(f"\n🏁 批量分析完成!")
    print("="*80)
    print(f"总文件数: {len(json_files)}")
    print(f"已处理数: {processed_count}")
    print(f"成功处理: {success_count}")
    print(f"处理失败: {failed_count}")
    print(f"成功率: {success_count/processed_count*100:.1f}%" if processed_count > 0 else "N/A")
    
    analyzer.save_checkpoint()
    analyzer.save_results()
    analyzer.save_summary_report()
    
    print(f"\n✅ 结果已保存到: {output_dir}")
    print(f"🔁 如需继续处理剩余文件，请重新运行此脚本")
    
    return True


def main():
    """主函数"""
    success = process_real_assessment_reports()
    
    if success:
        print("\n🎉 真实测评报告批量分析完成!")
        return 0
    else:
        print("\n❌ 真实测评报告批量分析失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())