#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超快速批量分析 - 无延迟版本
"""

import sys
import os
from pathlib import Path

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def ultra_fast_analysis():
    print("🚀🚀 超快速批量分析启动...")

    try:
        from batch_four_model_analysis import BatchFourModelAnalyzer

        # 创建超快分析器
        analyzer = BatchFourModelAnalyzer(
            models=["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        )

        print(f"🤖 使用模型: {', '.join(analyzer.models)}")
        print(f"⚡⚡ 超快设置: 无延迟，极速模式")

        # 查找输入文件
        results_dir = Path("results/results")
        if not results_dir.exists():
            print("❌ results目录不存在")
            return

        json_files = list(results_dir.glob("*.json"))
        if not json_files:
            print("❌ 没有找到JSON文件")
            return

        print(f"📁 找到 {len(json_files)} 个文件")

        # 检查断点信息
        if analyzer.load_progress():
            print(f"📂 发现断点继续信息:")
            print(f"   已完成: {len(analyzer.completed_files)} 个文件")
            print(f"   失败: {len(analyzer.failed_files)} 个文件")
        else:
            print("📂 未发现断点信息，从头开始")

        # 过滤已处理的文件
        remaining_files = [f for f in json_files if str(f) not in analyzer.completed_files and str(f) not in analyzer.failed_files]

        print(f"📊 剩余待处理文件: {len(remaining_files)} 个")

        if not remaining_files:
            print("✅ 所有文件已处理完成")
            return

        # 创建输出目录
        output_dir = Path("four_model_results")
        output_dir.mkdir(exist_ok=True)

        # 超快进度回调
        def ultra_fast_progress_callback(completed, total, result):
            success_rate = sum(1 for r in analyzer.results if r.get('success', False)) / len(analyzer.results) * 100 if analyzer.results else 0
            confidences = [r.get('confidence_analysis', {}).get('overall_confidence', 0) for r in analyzer.results if r.get('success', False)]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            completed_in_batch = len(analyzer.completed_files) + len(analyzer.failed_files)
            progress_pct = completed_in_batch/total*100
            eta_hours = (total - completed_in_batch) * 0.1 / 3600 if completed_in_batch > 0 else 0  # 估算完成时间
            print(f"🚀🚀 超快进度: {completed_in_batch}/{total} ({progress_pct:.1f}%) - 成功率: {success_rate:.1f}% - 置信度: {avg_confidence:.1f}% - 预计剩余: {eta_hours:.1f}小时")

        print(f"\n⚡⚡ 开始超快批量分析...")
        print(f"🏃‍♂️🏃‍♀️ 无延迟，极速处理")

        results = analyzer.analyze_batch(
            remaining_files,
            output_dir,
            progress_callback=ultra_fast_progress_callback,
            delay_between_files=0  # 完全无延迟
        )

        # 生成最终汇总
        successful = sum(1 for r in results if r['success'])
        print(f"\n🎯🎯 超快批量分析完成:")
        print(f"✅ 成功: {successful}/{len(results)}")
        print(f"📁 结果保存在: {output_dir}")

        if successful > 0:
            analyzer.generate_summary_report(results, output_dir)
            print(f"📋 汇总报告已生成: {output_dir}/four_model_batch_summary.md")

            # 生成当前进度汇总
            os.system("python generate_current_summary.py")

    except Exception as e:
        print(f"💥 超快批量分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ultra_fast_analysis()