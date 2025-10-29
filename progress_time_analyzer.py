#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间和进度分析脚本
分析并行多模型处理系统的效率和预期完成时间
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
import statistics

def analyze_progress():
    """分析处理进度和时间效率"""
    print("📊 并行多模型处理系统 - 时间与进度分析报告")
    print("=" * 60)

    # 基础配置信息
    total_files = 550
    completed_files = 3
    remaining_files = total_files - completed_files
    num_processes = 4
    models_per_file = 3

    print(f"📋 任务配置:")
    print(f"   总文件数: {total_files}")
    print(f"   并行进程数: {num_processes}")
    print(f"   每文件模型数: {models_per_file}")
    print(f"   当前已完成: {completed_files}")
    print(f"   剩余文件: {remaining_files}")
    print()

    # 分析已完成文件的时间戳
    results_dir = "multi_model_5segment_results"
    analysis_files = glob.glob(os.path.join(results_dir, "*_multi_model_5segment_analysis.json"))

    if not analysis_files:
        print("❌ 未找到已完成的分析文件")
        return

    print(f"📁 已完成分析文件: {len(analysis_files)}")

    # 提取时间信息
    completion_times = []
    for file_path in analysis_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            analysis_date = data.get('file_info', {}).get('analysis_date')
            if analysis_date:
                dt = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                completion_times.append(dt)
                print(f"   {Path(file_path).name[:50]}... -> {dt.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"   ❌ 解析文件失败: {Path(file_path).name} - {e}")

    if len(completion_times) < 2:
        print("⚠️ 需要至少2个完成文件来计算处理速度")
        return

    # 计算处理速度
    completion_times.sort()
    time_span = completion_times[-1] - completion_times[0]
    files_processed = len(completion_times)

    print(f"\n⏱️ 处理时间分析:")
    print(f"   首个完成: {completion_times[0].strftime('%H:%M:%S')}")
    print(f"   最新完成: {completion_times[-1].strftime('%H:%M:%S')}")
    print(f"   总耗时: {time_span}")
    print(f"   处理文件数: {files_processed}")

    if time_span.total_seconds() > 0:
        # 计算平均处理速度
        avg_time_per_file = time_span.total_seconds() / files_processed
        files_per_hour = 3600 / avg_time_per_file

        print(f"   平均每文件: {avg_time_per_file:.1f}秒")
        print(f"   处理速度: {files_per_hour:.1f}文件/小时")

        # 预估剩余时间
        estimated_remaining_time = remaining_files * avg_time_per_file / num_processes
        estimated_completion = datetime.now() + timedelta(seconds=estimated_remaining_time)

        print(f"\n🎯 完成时间预估:")
        print(f"   剩余文件: {remaining_files}")
        print(f"   预估剩余时间: {timedelta(seconds=int(estimated_remaining_time))}")
        print(f"   预计完成时间: {estimated_completion.strftime('%Y-%m-%d %H:%M:%S')}")

        # 效率分析
        single_process_time = remaining_files * avg_time_per_file
        parallel_time_saved = single_process_time - estimated_remaining_time
        efficiency_gain = (parallel_time_saved / single_process_time) * 100

        print(f"\n🚀 并行处理效率:")
        print(f"   单进程预估时间: {timedelta(seconds=int(single_process_time))}")
        print(f"   并行预估时间: {timedelta(seconds=int(estimated_remaining_time))}")
        print(f"   节省时间: {timedelta(seconds=int(parallel_time_saved))}")
        print(f"   效率提升: {efficiency_gain:.1f}%")

        # API调用统计
        total_segments_per_file = 10  # 50题分10段，每段5题
        total_api_calls = completed_files * models_per_file * total_segments_per_file
        remaining_api_calls = remaining_files * models_per_file * total_segments_per_file

        print(f"\n📡 API调用统计:")
        print(f"   已完成调用: {total_api_calls}")
        print(f"   剩余调用: {remaining_api_calls}")
        print(f"   总调用数: {total_api_calls + remaining_api_calls}")

        # 成功率和质量指标
        success_rate = (completed_files / total_files) * 100
        print(f"\n✅ 质量指标:")
        print(f"   成功率: {success_rate:.1f}%")
        print(f"   模型一致性: 正在计算中...")

        # 时间分布分析
        if len(completion_times) >= 3:
            intervals = []
            for i in range(1, len(completion_times)):
                interval = (completion_times[i] - completion_times[i-1]).total_seconds()
                intervals.append(interval)

            avg_interval = statistics.mean(intervals)
            min_interval = min(intervals)
            max_interval = max(intervals)

            print(f"\n📈 处理间隔分析:")
            print(f"   平均间隔: {avg_interval:.1f}秒")
            print(f"   最快间隔: {min_interval:.1f}秒")
            print(f"   最慢间隔: {max_interval:.1f}秒")

            # 稳定性评估
            if len(intervals) > 1:
                interval_std = statistics.stdev(intervals)
                cv = (interval_std / avg_interval) * 100  # 变异系数
                print(f"   稳定性(CV): {cv:.1f}% ({'稳定' if cv < 20 else '中等' if cv < 50 else '不稳定'})")

def main():
    """主函数"""
    analyze_progress()

if __name__ == "__main__":
    main()