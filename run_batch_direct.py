#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行批量分析
"""

import sys
import os
from pathlib import Path

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def run_direct_batch():
    print("🚀 直接运行批量分析...")

    try:
        from batch_four_model_analysis import BatchFourModelAnalyzer

        # 创建分析器
        analyzer = BatchFourModelAnalyzer(
            models=["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        )

        print(f"🤖 使用模型: {', '.join(analyzer.models)}")
        print(f"🔑 API密钥已设置: {analyzer.api_key[:10]}...")

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

        # 创建输出目录
        output_dir = Path("direct_batch_results")
        output_dir.mkdir(exist_ok=True)

        # 只处理前5个文件作为测试
        test_files = json_files[:5]
        print(f"🧪 测试前 {len(test_files)} 个文件")

        results = []
        for i, file in enumerate(test_files, 1):
            print(f"\n📈 进度: [{i}/{len(test_files)}] {file.name}")

            try:
                result = analyzer.analyze_single_file(file, output_dir)
                results.append(result)

                if result['success']:
                    confidence = result.get('overall_confidence', 0)
                    mbti = result.get('representative_mbti', 'N/A')
                    models = f"{len(result.get('successful_models', []))}/{result.get('total_models_attempted', 0)}"
                    print(f"✅ 成功 - 置信度: {confidence}% - MBTI: {mbti} - 模型: {models}")
                else:
                    print(f"❌ 失败 - {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"💥 异常 - {e}")
                results.append({
                    'file': str(file),
                    'success': False,
                    'error': str(e)
                })

        # 生成简单汇总
        successful = sum(1 for r in results if r['success'])
        print(f"\n📊 测试完成:")
        print(f"✅ 成功: {successful}/{len(results)}")
        print(f"📁 结果保存在: {output_dir}")

        # 如果成功，建议运行完整批量分析
        if successful > 0:
            print(f"\n🎯 测试成功！建议运行完整批量分析:")
            print(f"python batch_four_model_analysis.py results/results --delay 5")

    except Exception as e:
        print(f"💥 批量分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_direct_batch()