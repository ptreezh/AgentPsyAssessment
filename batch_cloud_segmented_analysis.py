#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量云评估器分段式心理评估分析器
使用Qwen云模型对多个测评报告进行分段处理，生成标准化的1-3-5评分Big5评估
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from cloud_segmented_analysis import CloudSegmentedPersonalityAnalyzer

class BatchCloudSegmentedAnalyzer:
    """批量云评估器分段分析器"""

    def __init__(self, model: str = "qwen-long", api_key: str = None, max_workers: int = 2):
        self.model = model
        self.api_key = api_key or "sk-ffd03518254b495b8d27e723cd413fc1"
        self.max_workers = max_workers
        self.results = []

    def analyze_single_file(self, input_file: Path, output_dir: Path) -> dict:
        """分析单个文件"""
        try:
            print(f"🔍 开始分析: {input_file.name}")

            # 创建分析器
            analyzer = CloudSegmentedPersonalityAnalyzer(
                model=self.model,
                api_key=self.api_key
            )

            # 执行分析
            result = analyzer.analyze_full_assessment(str(input_file))

            # 保存结果
            output_file = output_dir / f"{input_file.stem}_{self.model}_segmented.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # 生成摘要
            big5_scores = result['big_five_final_scores']
            summary = {
                'file': str(input_file),
                'output_file': str(output_file),
                'model': self.model,
                'success': True,
                'big5_final_scores': {trait: data['final_score'] for trait, data in big5_scores.items()},
                'mbti_type': result['mbti_assessment']['type'],
                'total_questions': result['file_info']['total_questions'],
                'segments_processed': result['file_info']['segments_count']
            }

            print(f"✅ 分析完成: {input_file.name}")
            print(f"   Big5: {summary['big5_final_scores']}")
            print(f"   MBTI: {summary['mbti_type']}")
            print(f"   输出: {output_file.name}")

            return summary

        except Exception as e:
            error_summary = {
                'file': str(input_file),
                'output_file': None,
                'model': self.model,
                'success': False,
                'error': str(e),
                'big5_final_scores': {},
                'mbti_type': None,
                'total_questions': 0,
                'segments_processed': 0
            }

            print(f"❌ 分析失败: {input_file.name} - {e}")
            return error_summary

    def analyze_batch(self, input_files: list[Path], output_dir: Path,
                     progress_callback=None) -> list[dict]:
        """批量分析文件"""
        print(f"🚀 开始批量分析 {len(input_files)} 个文件")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {self.model}")
        print(f"⚡ 并发数: {self.max_workers}")

        output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        completed = 0

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

                    if progress_callback:
                        progress_callback(completed, len(input_files), result)

                    # 显示进度
                    success = "✅" if result['success'] else "❌"
                    print(f"[{completed}/{len(input_files)}] {success} {file.name}")

                    # 添加延迟避免API限制
                    time.sleep(2)

                except Exception as e:
                    print(f"❌ 处理 {file.name} 时发生异常: {e}")
                    results.append({
                        'file': str(file),
                        'success': False,
                        'error': str(e)
                    })

        return results

    def generate_summary_report(self, results: list[dict], output_dir: Path):
        """生成汇总报告"""
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]

        # 统计Big5评分分布
        big5_stats = {}
        mbti_stats = {}

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

        # 生成汇总数据
        summary = {
            'summary': {
                'total_files': len(results),
                'successful': len(successful_results),
                'failed': len(failed_results),
                'success_rate': len(successful_results) / len(results) * 100 if results else 0,
                'model_used': self.model,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'big5_distribution': big5_stats,
            'mbti_distribution': mbti_stats,
            'detailed_results': results
        }

        # 保存JSON汇总
        json_summary = output_dir / f"batch_summary_{self.model}.json"
        with open(json_summary, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 生成Markdown报告
        md_content = f"""# 批量云评估器分段分析报告

**分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**使用模型:** {self.model}
**评分标准:** 1-3-5 (1=低, 3=中, 5=高)

## 汇总统计

- **总文件数:** {len(results)}
- **成功分析:** {len(successful_results)}
- **失败分析:** {len(failed_results)}
- **成功率:** {summary['summary']['success_rate']:.1f}%

## Big5评分分布

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
            md_content += f"- **{filename}** - Big5: {big5_str} - MBTI: {result['mbti_type']}\n"

        if failed_results:
            md_content += "\n## 失败的文件\n\n"
            for result in failed_results:
                filename = Path(result['file']).name
                md_content += f"- **{filename}** - 错误: {result.get('error', 'Unknown error')}\n"

        # 保存Markdown报告
        md_summary = output_dir / f"batch_report_{self.model}.md"
        with open(md_summary, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\n📊 汇总报告已生成:")
        print(f"   JSON: {json_summary}")
        print(f"   Markdown: {md_summary}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量云评估器分段式Big5分析')
    parser.add_argument('input_path', help='输入文件或目录路径')
    parser.add_argument('--model', default='qwen-long', choices=['qwen-long', 'qwen-max'],
                       help='使用的云模型')
    parser.add_argument('--output', default='batch_cloud_segmented_results', help='输出目录')
    parser.add_argument('--sample', type=int, help='采样文件数量')
    parser.add_argument('--filter', help='文件名过滤模式')
    parser.add_argument('--workers', type=int, default=2, help='并发工作数')

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
    analyzer = BatchCloudSegmentedAnalyzer(
        model=args.model,
        max_workers=args.workers
    )

    # 创建输出目录
    output_dir = Path(args.output) / args.model
    output_dir.mkdir(parents=True, exist_ok=True)

    # 执行批量分析
    def progress_callback(completed, total, result):
        print(f"📈 进度: {completed}/{total} ({completed/total*100:.1f}%)")

    results = analyzer.analyze_batch(input_files, output_dir, progress_callback)

    # 生成汇总报告
    print(f"\n📋 生成汇总报告...")
    analyzer.generate_summary_report(results, output_dir)

    # 最终统计
    successful = sum(1 for r in results if r['success'])
    print(f"\n🎉 批量分析完成!")
    print(f"✅ 成功: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"📁 结果保存在: {output_dir}")

if __name__ == "__main__":
    main()