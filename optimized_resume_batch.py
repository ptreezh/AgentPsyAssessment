#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化断点继续批量分析 - 5题分段 + 1秒延迟 + 智能缓存
"""

import sys
import os
import json
import hashlib
from pathlib import Path

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def optimized_resume_batch():
    print("🚀 优化断点继续批量分析 - 5题分段 + 1秒延迟")

    try:
        # 导入并修改原有的批量分析器
        import importlib
        import batch_four_model_analysis

        # 重新加载模块以应用我们的修改
        importlib.reload(batch_four_model_analysis)

        # 创建优化分析器
        analyzer = batch_four_model_analysis.BatchFourModelAnalyzer(
            models=["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        )

        print(f"🤖 使用模型: {', '.join(analyzer.models)}")
        print(f"🔑 API密钥已设置")

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
        output_dir = Path("optimized_four_model_results")
        output_dir.mkdir(exist_ok=True)

        # 优化进度回调
        def optimized_progress_callback(completed, total, result):
            success_rate = sum(1 for r in analyzer.results if r.get('success', False)) / len(analyzer.results) * 100 if analyzer.results else 0
            confidences = [r.get('confidence_analysis', {}).get('overall_confidence', 0) for r in analyzer.results if r.get('success', False)]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            completed_in_batch = len(analyzer.completed_files) + len(analyzer.failed_files)
            progress_pct = completed_in_batch / total * 100
            eta_hours = (total - completed_in_batch) * 0.2 / 3600 if completed_in_batch > 0 else 0
            print(f"🚀 优化进度: {completed_in_batch}/{total} ({progress_pct:.1f}%) - 成功率: {success_rate:.1f}% - 平均置信度: {avg_confidence:.1f}% - 预计剩余: {eta_hours:.1f}小时")

        print(f"\n🎯 开始优化批量分析...")
        print(f"⚡ 优化配置: 5题分段, 1秒延迟, 智能缓存")
        print(f"🔧 预期提升: 分段减少50%, 延迟减少93%")

        # 临时修改分析器配置
        original_segment_size = getattr(analyzer, 'segment_size', 2)
        analyzer.segment_size = 5  # 5题分段

        # 执行批量分析
        results = analyzer.analyze_batch(
            remaining_files,
            output_dir,
            progress_callback=optimized_progress_callback,
            delay_between_files=1  # 1秒延迟
        )

        # 恢复原始配置
        analyzer.segment_size = original_segment_size

        # 生成最终汇总
        successful = sum(1 for r in results if r['success'])
        print(f"\n📊 优化批量分析完成:")
        print(f"✅ 成功: {successful}/{len(results)}")
        print(f"📁 结果保存在: {output_dir}")

        if successful > 0:
            analyzer.generate_summary_report(results, output_dir)
            print(f"📋 汇总报告已生成: {output_dir}/four_model_batch_summary.md")

            # 生成当前进度汇总
            os.system("python generate_current_summary.py")

            # 计算优化效果
            original_segments_per_file = 50 // 2  # 原来25分段
            new_segments_per_file = 50 // 5  # 现在10分段
            segment_reduction = original_segments_per_file / new_segments_per_file

            print(f"\n🎯 优化效果:")
            print(f"   分段数量: {original_segments_per_file} → {new_segments_per_file} (减少 {segment_reduction:.1f}倍)")
            print(f"   延迟时间: 15秒 → 1秒 (减少15倍)")
            print(f"   预期总体提升: {segment_reduction * 15:.1f}倍")

    except Exception as e:
        print(f"💥 优化批量分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    optimized_resume_batch()