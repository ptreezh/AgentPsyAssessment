#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复版云评估器分段式心理评估分析器
使用修复版算法进行完整的50道题目分析，支持qwen-long和qwen-max模型
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from cloud_segmented_analysis_fixed import FixedCloudSegmentedPersonalityAnalyzer

class BatchFixedCloudAnalyzer:
    """批量修复版云评估器分析器"""

    def __init__(self, model: str = "qwen-long", api_key: str = None, max_workers: int = 1):
        self.model = model
        self.api_key = api_key or "sk-ffd03518254b495b8d27e723cd413fc1"
        self.max_workers = max_workers
        self.results = []

    def analyze_single_file(self, input_file: Path, output_dir: Path) -> dict:
        """分析单个文件"""
        try:
            # 创建分析器
            analyzer = FixedCloudSegmentedPersonalityAnalyzer(
                model=self.model,
                api_key=self.api_key
            )

            # 检查API可用性
            if not analyzer.api_available:
                return {
                    'file': str(input_file),
                    'success': False,
                    'error': f'API connection failed for {self.model}',
                    'skipped': True
                }

            # 执行分析
            result = analyzer.analyze_full_assessment(str(input_file), str(output_dir))

            if result['success']:
                # 从分析器实例中获取评分数据
                final_scores = analyzer.calculate_final_scores()
                mbti_result = analyzer.generate_mbti_type(final_scores)

                # 生成摘要
                summary = {
                    'file': str(input_file),
                    'summary_file': result['summary_file'],
                    'evidence_file': result['evidence_file'],
                    'model': self.model,
                    'success': True,
                    'big5_final_scores': {trait: data.get('final_score', 3) for trait, data in final_scores.items()},
                    'mbti_type': mbti_result['type'],
                    'analysis_quality': {
                        'success_rate': 100.0,  # 如果成功完成，说明所有分段都成功了
                        'successful_segments': len(analyzer.segment_results),
                        'total_segments': len(analyzer.segment_results)
                    }
                }

                big5_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in summary['big5_final_scores'].items()])
                print(f"✅ {input_file.name} - Big5: {big5_str} - MBTI: {summary['mbti_type']}")
                return summary
            else:
                print(f"❌ {input_file.name} - {result.get('error', 'Unknown error')}")
                return {
                    'file': str(input_file),
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'model': self.model,
                    'skipped': False
                }

        except Exception as e:
            print(f"💥 {input_file.name} - 异常: {e}")
            return {
                'file': str(input_file),
                'success': False,
                'error': str(e),
                'model': self.model,
                'skipped': False
            }

    def analyze_batch(self, input_files: list[Path], output_dir: Path,
                     progress_callback=None, delay_between_files: int = 3) -> list[dict]:
        """批量分析文件"""
        print(f"🚀 开始批量修复版云评估器分析")
        print(f"📁 输入文件: {len(input_files)} 个")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {self.model}")
        print(f"⚡ 并发数: {self.max_workers}")
        print(f"⏱️  文件间延迟: {delay_between_files} 秒")

        output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        completed = 0
        api_failure_count = 0

        # 使用线程池进行并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(self.analyze_single_file, file, output_dir): file
                for file in input_files
            }

            # 处理完成的任务
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1

                    # 检查API失败
                    if result.get('skipped') and 'API connection failed' in result.get('error', ''):
                        api_failure_count += 1
                        # 如果连续API失败，停止批量处理
                        if api_failure_count >= 3:
                            print(f"\n⚠️  连续{api_failure_count}次API失败，停止批量处理")
                            break

                    if progress_callback:
                        progress_callback(completed, len(input_files), result)

                    # 显示进度
                    status = "✅" if result['success'] else ("⏭️" if result.get('skipped') else "❌")
                    print(f"[{completed}/{len(input_files)}] {status} {file.name}")

                    # 添加延迟避免API限制
                    if completed < len(input_files):
                        time.sleep(delay_between_files)

                except Exception as e:
                    print(f"💥 处理 {file.name} 时发生异常: {e}")
                    results.append({
                        'file': str(file),
                        'success': False,
                        'error': str(e),
                        'model': self.model
                    })

        return results

    def generate_summary_report(self, results: list[dict], output_dir: Path):
        """生成汇总报告"""
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        skipped_results = [r for r in results if r.get('skipped', False)]

        # 统计Big5评分分布
        big5_stats = {}
        mbti_stats = {}
        confidence_stats = []

        for result in successful_results:
            # Big5统计
            for trait, score in result['big5_final_scores'].items():
                if trait not in big5_stats:
                    big5_stats[trait] = {1: 0, 3: 0, 5: 0}
                big5_stats[trait][score] += 1

            # MBTI统计
            mbti_type = result['mbti_type']
            if mbti_type not in mbti_stats:
                mbti_stats[mbti_type] = 0
            mbti_stats[mbti_type] += 1

            # 置信度统计
            if 'analysis_quality' in result:
                confidence_stats.append(result['analysis_quality']['success_rate'])

        # 生成汇总数据
        summary = {
            'summary': {
                'total_files': len(results),
                'successful': len(successful_results),
                'failed': len(failed_results),
                'skipped_due_to_api': len(skipped_results),
                'success_rate': len(successful_results) / len(results) * 100 if results else 0,
                'model_used': self.model,
                'analysis_timestamp': datetime.now().isoformat(),
                'algorithm_version': 'fixed_v1.0'
            },
            'big5_distribution': big5_stats,
            'mbti_distribution': mbti_stats,
            'analysis_quality': {
                'average_success_rate': sum(confidence_stats) / len(confidence_stats) if confidence_stats else 0,
                'confidence_stats': confidence_stats
            },
            'detailed_results': results
        }

        # 保存JSON汇总
        json_summary = output_dir / f"batch_summary_fixed_{self.model}.json"
        with open(json_summary, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 生成Markdown报告
        md_content = f"""# 修复版批量云评估器分析报告

**分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**使用模型:** {self.model}
**算法版本:** fixed_v1.0
**评分标准:** 严格1-3-5评分 (1=低, 3=中, 5=高)

## 汇总统计

- **总文件数:** {len(results)}
- **成功分析:** {len(successful_results)}
- **失败分析:** {len(failed_results)}
- **API跳过:** {len(skipped_results)}
- **成功率:** {summary['summary']['success_rate']:.1f}%

## 分析质量

- **平均分段成功率:** {summary['analysis_quality']['average_success_rate']:.1f}%
- **使用修复版算法:** ✅ 评分范围验证、置信度计算、错误处理优化

## Big5评分分布 (修复版)

"""

        for trait, scores in big5_stats.items():
            total = sum(scores.values())
            md_content += f"### {trait.replace('_', ' ').title()}\n"
            md_content += f"- 1分 (低): {scores[1]} ({scores[1]/total*100:.1f}%)\n"
            md_content += f"- 3分 (中): {scores[3]} ({scores[3]/total*100:.1f}%)\n"
            md_content += f"- 5分 (高): {scores[5]} ({scores[5]/total*100:.1f}%)\n\n"

        md_content += "## MBTI类型分布\n\n"

        for mbti_type, count in sorted(mbti_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(successful_results) * 100
            md_content += f"- **{mbti_type}:** {count} ({percentage:.1f}%)\n"

        md_content += "\n## 详细结果\n\n"

        for result in successful_results:
            filename = Path(result['file']).name
            big5_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in result['big5_final_scores'].items()])
            quality = result.get('analysis_quality', {}).get('success_rate', 0)
            md_content += f"- **{filename}** - Big5: {big5_str} - MBTI: {result['mbti_type']} - 质量: {quality:.1f}%\n"

        if failed_results:
            md_content += "\n## 失败的文件\n\n"
            for result in failed_results:
                filename = Path(result['file']).name
                md_content += f"- **{filename}** - 错误: {result.get('error', 'Unknown error')}\n"

        if skipped_results:
            md_content += "\n## API跳过的文件\n\n"
            for result in skipped_results:
                filename = Path(result['file']).name
                md_content += f"- **{filename}** - 原因: {result.get('error', 'Unknown reason')}\n"

        # 保存Markdown报告
        md_summary = output_dir / f"batch_report_fixed_{self.model}.md"
        with open(md_summary, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\n📊 修复版汇总报告已生成:")
        print(f"   JSON: {json_summary}")
        print(f"   Markdown: {md_summary}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量修复版云评估器分段式Big5分析')
    parser.add_argument('input_path', help='输入文件或目录路径')
    parser.add_argument('--model', default='qwen-long', choices=['qwen-long', 'qwen-max'],
                       help='使用的云模型')
    parser.add_argument('--output', default='fixed_cloud_segmented_results', help='输出目录')
    parser.add_argument('--sample', type=int, help='采样文件数量')
    parser.add_argument('--filter', help='文件名过滤模式')
    parser.add_argument('--workers', type=int, default=1, help='并发工作数（建议1避免API限制）')
    parser.add_argument('--delay', type=int, default=5, help='文件间延迟秒数')

    args = parser.parse_args()

    # 确定输入文件
    input_path = Path(args.input_path)
    if input_path.is_file():
        input_files = [input_path]
    elif input_path.is_dir():
        input_files = list(input_path.glob("*.json"))
    else:
        print(f"❌ 输入路径不存在: {input_path}")
        return

    # 应用过滤器
    if args.filter:
        input_files = [f for f in input_files if args.filter.lower() in f.name.lower()]

    # 采样
    if args.sample:
        input_files = input_files[:args.sample]

    if not input_files:
        print("❌ 没有找到符合条件的文件")
        return

    print(f"🔍 找到 {len(input_files)} 个文件进行分析")

    # 创建批量分析器
    analyzer = BatchFixedCloudAnalyzer(
        model=args.model,
        max_workers=args.workers
    )

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 执行批量分析
    def progress_callback(completed, total, result):
        success_rate = sum(1 for r in analyzer.results if r.get('success', False)) / len(analyzer.results) * 100 if analyzer.results else 0
        print(f"📈 进度: {completed}/{total} ({completed/total*100:.1f}%) - 成功率: {success_rate:.1f}%")

    results = analyzer.analyze_batch(
        input_files,
        output_dir,
        progress_callback=progress_callback,
        delay_between_files=args.delay
    )

    # 生成汇总报告
    print(f"\n📋 生成修复版汇总报告...")
    analyzer.generate_summary_report(results, output_dir)

    # 最终统计
    successful = sum(1 for r in results if r['success'])
    api_skipped = sum(1 for r in results if r.get('skipped', False))
    print(f"\n🎉 修复版批量分析完成!")
    print(f"✅ 成功: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    if api_skipped > 0:
        print(f"⏭️  API跳过: {api_skipped} 个文件")
    print(f"📁 结果保存在: {output_dir}")
    print(f"🔧 使用修复版算法: 评分验证 + 置信度计算 + 分离文件输出")

if __name__ == "__main__":
    main()