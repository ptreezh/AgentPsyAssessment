#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量多模型置信度心理评估分析器
使用多个云模型进行比较分析，基于模型间一致性计算置信度
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from multi_model_confidence_analyzer import MultiModelConfidenceAnalyzer

class BatchMultiModelAnalyzer:
    """批量多模型置信度分析器"""

    def __init__(self, models: list = None, api_key: str = None, max_workers: int = 1):
        self.models = models or ["qwen-long", "qwen-max"]
        self.api_key = api_key or "sk-ffd03518254b495b8d27e723cd413fc1"
        self.max_workers = max_workers
        self.results = []

    def analyze_single_file(self, input_file: Path, output_dir: Path) -> dict:
        """分析单个文件的多模型置信度"""
        try:
            # 创建多模型分析器
            analyzer = MultiModelConfidenceAnalyzer(
                models=self.models,
                api_key=self.api_key
            )

            # 执行多模型分析
            result = analyzer.analyze_with_multiple_models(input_file, output_dir)

            if result['success']:
                confidence = result['confidence_analysis']['overall_confidence']
                successful_models = result['confidence_analysis']['successful_models']

                # 生成简化摘要
                summary = {
                    'file': str(input_file),
                    'success': True,
                    'overall_confidence': confidence,
                    'successful_models': successful_models,
                    'total_models_attempted': len(self.models),
                    'big5_confidence': result['confidence_analysis']['big5_confidence'],
                    'mbti_confidence': result['confidence_analysis']['mbti_confidence'],
                    'most_common_mbti': result['confidence_analysis']['mbti_confidence'].get('most_common_type', 'N/A'),
                    'agreement_level': result['confidence_analysis']['mbti_confidence'].get('agreement_level', 'N/A')
                }

                # 获取第一个成功模型的结果作为代表性评分
                if successful_models:
                    first_success_model = successful_models[0]
                    model_result = result['multi_model_results'][first_success_model]
                    summary['representative_big5_scores'] = model_result['big5_scores']
                    summary['representative_mbti'] = model_result['mbti_type']

                big5_str = ""
                if 'representative_big5_scores' in summary:
                    big5_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in summary['representative_big5_scores'].items()])

                print(f"✅ {input_file.name} - 置信度: {confidence}% - MBTI: {summary.get('representative_mbti', 'N/A')} ({summary['agreement_level']})")
                return summary
            else:
                print(f"❌ {input_file.name} - 多模型分析失败")
                return {
                    'file': str(input_file),
                    'success': False,
                    'error': 'No successful model analysis',
                    'models_attempted': self.models
                }

        except Exception as e:
            print(f"💥 {input_file.name} - 异常: {e}")
            return {
                'file': str(input_file),
                'success': False,
                'error': str(e),
                'models_attempted': self.models
            }

    def analyze_batch(self, input_files: list[Path], output_dir: Path,
                     progress_callback=None, delay_between_files: int = 10) -> list[dict]:
        """批量分析文件的多模型置信度"""
        print(f"🚀 开始批量多模型置信度分析")
        print(f"📁 输入文件: {len(input_files)} 个")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {', '.join(self.models)}")
        print(f"⚡ 并发数: {self.max_workers}")
        print(f"⏱️  文件间延迟: {delay_between_files} 秒")

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
                    status = "✅" if result['success'] else "❌"
                    confidence_str = f" (置信度: {result['overall_confidence']}%)" if result['success'] else ""
                    print(f"[{completed}/{len(input_files)}] {status} {file.name}{confidence_str}")

                    # 添加延迟避免API限制
                    if completed < len(input_files):
                        print(f"⏳ 等待 {delay_between_files} 秒后处理下一个文件...")
                        time.sleep(delay_between_files)

                except Exception as e:
                    print(f"💥 处理 {file.name} 时发生异常: {e}")
                    results.append({
                        'file': str(file),
                        'success': False,
                        'error': str(e),
                        'models_attempted': self.models
                    })
                    completed += 1

        return results

    def generate_summary_report(self, results: list[dict], output_dir: Path):
        """生成多模型批量分析汇总报告"""
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]

        # 统计数据
        overall_confidences = [r['overall_confidence'] for r in successful_results]
        avg_confidence = sum(overall_confidences) / len(overall_confidences) if overall_confidences else 0

        # 统计Big5评分分布（使用代表性评分）
        big5_stats = {}
        mbti_stats = {}
        confidence_distribution = {'高度一致': 0, '中等一致': 0, '低度一致': 0, '不一致': 0}

        for result in successful_results:
            # Big5统计
            if 'representative_big5_scores' in result:
                for trait, score in result['representative_big5_scores'].items():
                    if trait not in big5_stats:
                        big5_stats[trait] = {1: 0, 3: 0, 5: 0}
                    big5_stats[trait][score] += 1

            # MBTI统计
            if 'representative_mbti' in result:
                mbti_type = result['representative_mbti']
                if mbti_type not in mbti_stats:
                    mbti_stats[mbti_type] = 0
                mbti_stats[mbti_type] += 1

            # 置信度分布统计
            agreement_level = result.get('agreement_level', '不一致')
            if agreement_level in confidence_distribution:
                confidence_distribution[agreement_level] += 1

        # 生成汇总数据
        summary = {
            'summary': {
                'total_files': len(results),
                'successful': len(successful_results),
                'failed': len(failed_results),
                'success_rate': len(successful_results) / len(results) * 100 if results else 0,
                'models_used': self.models,
                'analysis_timestamp': datetime.now().isoformat(),
                'algorithm_version': 'multi_model_confidence_v1.0'
            },
            'confidence_statistics': {
                'average_confidence': round(avg_confidence, 1),
                'confidence_distribution': confidence_distribution,
                'high_confidence_count': confidence_distribution['高度一致'],
                'medium_confidence_count': confidence_distribution['中等一致'],
                'low_confidence_count': confidence_distribution['低度一致'],
                'inconsistent_count': confidence_distribution['不一致']
            },
            'big5_distribution': big5_stats,
            'mbti_distribution': mbti_stats,
            'detailed_results': results
        }

        # 保存JSON汇总
        json_summary = output_dir / f"batch_multi_model_summary.json"
        with open(json_summary, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 生成Markdown报告
        self.generate_markdown_report(summary, output_dir)

        print(f"\n📊 多模型批量分析汇总报告已生成:")
        print(f"   JSON: {json_summary}")
        print(f"   Markdown: {output_dir / 'batch_multi_model_report.md'}")

    def generate_markdown_report(self, summary: dict, output_dir: Path):
        """生成Markdown格式的多模型批量分析报告"""
        summary_stats = summary['summary']
        confidence_stats = summary['confidence_statistics']
        big5_stats = summary['big5_distribution']
        mbti_stats = summary['mbti_distribution']

        md_content = f"""# 批量多模型置信度分析报告

## 基本信息

- **分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **使用模型:** {', '.join(summary_stats['models_used'])}
- **算法版本:** multi_model_confidence_v1.0
- **评分标准:** 严格1-3-5评分 (1=低, 3=中, 5=高)
- **置信度计算:** 基于多模型间一致性

## 汇总统计

- **总文件数:** {summary_stats['total_files']}
- **成功分析:** {summary_stats['successful']}
- **失败分析:** {summary_stats['failed']}
- **成功率:** {summary_stats['success_rate']:.1f}%

## 置信度统计

- **平均置信度:** {confidence_stats['average_confidence']}%
- **高度一致 (≥80%):** {confidence_stats['high_confidence_count']} 个文件
- **中等一致 (60-79%):** {confidence_stats['medium_confidence_count']} 个文件
- **低度一致 (40-59%):** {confidence_stats['low_confidence_count']} 个文件
- **不一致 (<40%):** {confidence_stats['inconsistent_count']} 个文件

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
            percentage = count / len(mbti_stats) * 100 if mbti_stats else 0
            md_content += f"- **{mbti_type}:** {count} ({percentage:.1f}%)\n"

        md_content += "\n## 详细结果\n\n"

        for result in summary['detailed_results']:
            if result['success']:
                filename = Path(result['file']).name
                confidence = result['overall_confidence']
                mbti = result.get('representative_mbti', 'N/A')
                agreement = result.get('agreement_level', 'N/A')
                models = f"{len(result['successful_models'])}/{result['total_models_attempted']}"

                big5_str = ""
                if 'representative_big5_scores' in result:
                    big5_str = " - Big5: " + ", ".join([f"{trait[0].upper()}:{score}" for trait, score in result['representative_big5_scores'].items()])

                md_content += f"- **{filename}** - 置信度: {confidence}% - MBTI: {mbti} ({agreement}) - 模型: {models}{big5_str}\n"

        if failed_results:
            md_content += "\n## 失败的文件\n\n"
            for result in failed_results:
                filename = Path(result['file']).name
                md_content += f"- **{filename}** - 错误: {result.get('error', 'Unknown error')}\n"

        # 保存Markdown报告
        md_file = output_dir / "batch_multi_model_report.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量多模型置信度Big5分析')
    parser.add_argument('input_path', help='输入文件或目录路径')
    parser.add_argument('--models', nargs='+', default=['qwen-long', 'qwen-max'],
                       help='使用的云模型列表')
    parser.add_argument('--output', default='multi_model_confidence_results', help='输出目录')
    parser.add_argument('--sample', type=int, help='采样文件数量')
    parser.add_argument('--filter', help='文件名过滤模式')
    parser.add_argument('--workers', type=int, default=1, help='并发工作数（建议1避免API限制）')
    parser.add_argument('--delay', type=int, default=15, help='文件间延迟秒数（多模型分析需要更长延迟）')

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

    print(f"🔍 找到 {len(input_files)} 个文件进行多模型分析")

    # 创建批量多模型分析器
    analyzer = BatchMultiModelAnalyzer(
        models=args.models,
        max_workers=args.workers
    )

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 执行批量分析
    def progress_callback(completed, total, result):
        success_rate = sum(1 for r in analyzer.results if r.get('success', False)) / len(analyzer.results) * 100 if analyzer.results else 0
        avg_confidence = sum(r.get('overall_confidence', 0) for r in analyzer.results if r.get('success', False)) / len([r for r in analyzer.results if r.get('success', False)]) if analyzer.results and any(r.get('success', False) for r in analyzer.results) else 0
        print(f"📈 进度: {completed}/{total} ({completed/total*100:.1f}%) - 成功率: {success_rate:.1f}% - 平均置信度: {avg_confidence:.1f}%")

    results = analyzer.analyze_batch(
        input_files,
        output_dir,
        progress_callback=progress_callback,
        delay_between_files=args.delay
    )

    # 生成汇总报告
    print(f"\n📋 生成多模型置信度汇总报告...")
    analyzer.generate_summary_report(results, output_dir)

    # 最终统计
    successful = sum(1 for r in results if r['success'])
    avg_confidence = sum(r.get('overall_confidence', 0) for r in results if r['success']) / len([r for r in results if r['success']]) if successful > 0 else 0
    high_confidence = sum(1 for r in results if r['success'] and r.get('overall_confidence', 0) >= 80)

    print(f"\n🎉 多模型批量分析完成!")
    print(f"✅ 成功: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"📊 平均置信度: {avg_confidence:.1f}%")
    print(f"🎯 高置信度文件: {high_confidence} 个")
    print(f"📁 结果保存在: {output_dir}")
    print(f"🔧 使用多模型置信度算法: 模型间一致性比较")

if __name__ == "__main__":
    main()