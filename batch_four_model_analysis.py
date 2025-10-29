#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四模型批量云评估器分析器
使用 qwen-max, deepseek-v3.2-exp, Moonshot-Kimi-K2-Instruct, claude-3.5-sonnet
支持断点继续功能
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from multi_model_confidence_analyzer import MultiModelConfidenceAnalyzer
import hashlib

class BatchFourModelAnalyzer:
    """四模型批量分析器 - 支持断点继续"""

    def __init__(self, models: list = None, api_key: str = None, max_workers: int = 1):
        # 暂时移除Claude API，使用三个可用的DashScope模型
        self.models = models or ["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        # 强制设置新的API密钥
        self.api_key = api_key or "sk-3f16ac9d87e34ca88bf3925c3651624f"
        self.max_workers = max_workers
        self.results = []

        # 断点继续相关
        self.progress_file = Path("batch_four_model_progress.json")
        self.completed_files = set()
        self.failed_files = set()
        self.start_time = None

    def load_progress(self):
        """加载断点继续信息"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    self.completed_files = set(progress_data.get('completed_files', []))
                    self.failed_files = set(progress_data.get('failed_files', []))
                    self.start_time = progress_data.get('start_time')

                print(f"📂 发现断点继续信息:")
                print(f"   已完成: {len(self.completed_files)} 个文件")
                print(f"   失败: {len(self.failed_files)} 个文件")
                if self.start_time:
                    start_dt = datetime.fromisoformat(self.start_time)
                    print(f"   开始时间: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            except Exception as e:
                print(f"⚠️  无法加载断点信息: {e}")
                return False
        return False

    def save_progress(self):
        """保存断点继续信息"""
        progress_data = {
            'models': self.models,
            'completed_files': list(self.completed_files),
            'failed_files': list(self.failed_files),
            'start_time': self.start_time or datetime.now().isoformat(),
            'last_update': datetime.now().isoformat(),
            'total_processed': len(self.completed_files) + len(self.failed_files)
        }

        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存断点信息失败: {e}")

    def analyze_single_file(self, input_file: Path, output_dir: Path) -> dict:
        """分析单个文件的四模型置信度"""
        file_hash = hashlib.md5(str(input_file).encode('utf-8')).hexdigest()[:8]

        try:
            # 检查是否已完成
            if str(input_file) in self.completed_files:
                # 检查输出文件是否存在
                model_output_dir = output_dir / "multi_model_results"
                summary_file = model_output_dir / f"{input_file.stem}_multi_model_confidence.json"

                if summary_file.exists():
                    print(f"⏭️  跳过已完成文件: {input_file.name}")
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            existing_result = json.load(f)
                        return {
                            'file': str(input_file),
                            'success': True,
                            'skipped': True,
                            'existing_result': existing_result
                        }
                    except:
                        print(f"⚠️  已完成文件结果损坏，重新分析: {input_file.name}")
                else:
                    print(f"⚠️  标记完成但结果文件不存在，重新分析: {input_file.name}")

            print(f"🔍 开始分析: {input_file.name} [{file_hash}]")

            # 创建多模型分析器
            analyzer = MultiModelConfidenceAnalyzer(
                models=self.models,
                api_key=self.api_key
            )

            # 执行四模型分析
            result = analyzer.analyze_with_multiple_models(input_file, output_dir)

            if result['success']:
                confidence = result['confidence_analysis']['overall_confidence']
                successful_models = result['confidence_analysis']['successful_models']

                # 生成简化摘要
                summary = {
                    'file': str(input_file),
                    'file_hash': file_hash,
                    'success': True,
                    'overall_confidence': confidence,
                    'successful_models': successful_models,
                    'total_models_attempted': len(self.models),
                    'big5_confidence': result['confidence_analysis']['big5_confidence'],
                    'mbti_confidence': result['confidence_analysis']['mbti_confidence'],
                    'most_common_mbti': result['confidence_analysis']['mbti_confidence'].get('most_common_type', 'N/A'),
                    'agreement_level': result['confidence_analysis']['mbti_confidence'].get('agreement_level', 'N/A'),
                    'analysis_timestamp': datetime.now().isoformat()
                }

                # 获取代表性评分（使用第一个成功模型）
                if successful_models:
                    first_success_model = successful_models[0]
                    model_result = result['multi_model_results'][first_success_model]
                    summary['representative_big5_scores'] = model_result['big5_scores']
                    summary['representative_mbti'] = model_result['mbti_type']

                big5_str = ""
                if 'representative_big5_scores' in summary:
                    big5_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in summary['representative_big5_scores'].items()])

                print(f"✅ {input_file.name} - 置信度: {confidence}% - MBTI: {summary.get('representative_mbti', 'N/A')} ({summary['agreement_level']})")

                # 标记为已完成
                self.completed_files.add(str(input_file))

                return summary
            else:
                print(f"❌ {input_file.name} - 四模型分析失败")

                # 标记为失败
                self.failed_files.add(str(input_file))

                return {
                    'file': str(input_file),
                    'success': False,
                    'error': 'Multi-model analysis failed',
                    'models_attempted': self.models
                }

        except Exception as e:
            print(f"💥 {input_file.name} - 异常: {e}")

            # 标记为失败
            self.failed_files.add(str(input_file))

            return {
                'file': str(input_file),
                'success': False,
                'error': str(e),
                'models_attempted': self.models
            }

    def analyze_batch(self, input_files: list[Path], output_dir: Path,
                     progress_callback=None, delay_between_files: int = 15) -> list[dict]:
        """批量分析文件的四模型置信度"""
        print(f"🚀 开始四模型批量云评估分析")
        print(f"📁 输入文件: {len(input_files)} 个")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {', '.join(self.models)}")
        print(f"⚡ 并发数: {self.max_workers}")
        print(f"⏱️  文件间延迟: {delay_between_files} 秒")
        print(f"🔄 支持断点继续: ✅")

        output_dir.mkdir(parents=True, exist_ok=True)

        # 加载断点继续信息
        has_progress = self.load_progress()
        if has_progress:
            # 过滤已完成的文件
            remaining_files = [f for f in input_files if str(f) not in self.completed_files]
            print(f"📊 过滤后剩余文件: {len(remaining_files)} 个")
        else:
            remaining_files = input_files
            self.start_time = datetime.now().isoformat()

        if not remaining_files:
            print("✅ 所有文件已完成分析")
            return []

        results = []
        completed = 0

        # 使用单线程处理以避免API限制
        for i, file in enumerate(remaining_files, 1):
            print(f"\n📈 进度: [{i}/{len(remaining_files)}] 剩余: {len(remaining_files) - i}")

            try:
                result = self.analyze_single_file(file, output_dir)
                results.append(result)
                completed += 1

                # 更新进度
                if progress_callback:
                    progress_callback(len(self.completed_files) + len(self.failed_files), len(input_files), result)

                # 保存断点信息
                self.save_progress()

                # 添加延迟避免API限制
                if i < len(remaining_files):
                    print(f"⏳ 等待 {delay_between_files} 秒后处理下一个文件...")
                    time.sleep(delay_between_files)

            except KeyboardInterrupt:
                print(f"\n⚠️  用户中断，正在保存进度...")
                self.save_progress()
                print("💾 进度已保存，可使用相同命令继续")
                break
            except Exception as e:
                print(f"💥 处理 {file.name} 时发生异常: {e}")
                self.failed_files.add(str(file))
                self.save_progress()

        return results

    def generate_summary_report(self, results: list[dict], output_dir: Path):
        """生成四模型批量分析汇总报告"""
        successful_results = [r for r in results if r['success'] and not r.get('skipped', False)]
        failed_results = [r for r in results if not r['success']]
        skipped_results = [r for r in results if r.get('skipped', False)]

        # 统计数据
        overall_confidences = [r['overall_confidence'] for r in successful_results if 'overall_confidence' in r]
        avg_confidence = sum(overall_confidences) / len(overall_confidences) if overall_confidences else 0

        # 统计Big5评分分布
        big5_stats = {}
        mbti_stats = {}
        confidence_distribution = {'高度一致': 0, '中等一致': 0, '低度一致': 0, '不一致': 0}

        for result in successful_results:
            # Big5统计
            if 'representative_big5_scores' in result:
                for trait, score in result['representative_big5_scores'].items():
                    if trait not in big5_stats:
                        big5_stats[trait] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
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
                'skipped': len(skipped_results),
                'success_rate': len(successful_results) / len(results) * 100 if results else 0,
                'models_used': self.models,
                'analysis_timestamp': datetime.now().isoformat(),
                'algorithm_version': 'four_model_confidence_v1.0',
                'start_time': self.start_time,
                'completion_time': datetime.now().isoformat()
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
        json_summary = output_dir / f"batch_four_model_summary.json"
        with open(json_summary, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 生成Markdown报告
        self.generate_markdown_report(summary, output_dir)

        print(f"\n📊 四模型批量分析汇总报告已生成:")
        print(f"   JSON: {json_summary}")
        print(f"   Markdown: {output_dir / 'batch_four_model_report.md'}")

    def generate_markdown_report(self, summary: dict, output_dir: Path):
        """生成Markdown格式的四模型批量分析报告"""
        summary_stats = summary['summary']
        confidence_stats = summary['confidence_statistics']
        big5_stats = summary['big5_distribution']
        mbti_stats = summary['mbti_distribution']

        md_content = f"""# 四模型批量云评估分析报告

## 基本信息

- **分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **使用模型:** {', '.join(summary_stats['models_used'])}
- **算法版本:** four_model_confidence_v1.0
- **评分标准:** 严格1-3-5评分 (1=低, 3=中, 5=高)
- **置信度计算:** 基于四模型间一致性
- **断点继续:** 支持

## 汇总统计

- **总文件数:** {summary_stats['total_files']}
- **成功分析:** {summary_stats['successful']}
- **失败分析:** {summary_stats['failed']}
- **跳过文件:** {summary_stats['skipped']}
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
            for score in sorted(scores.keys()):
                count = scores[score]
                if count > 0:
                    percentage = count / total * 100
                    md_content += f"- {score}分: {count} ({percentage:.1f}%)\n"
            md_content += "\n"

        md_content += "## MBTI类型分布\n\n"

        for mbti_type, count in sorted(mbti_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(mbti_stats) * 100 if mbti_stats else 0
            md_content += f"- **{mbti_type}:** {count} ({percentage:.1f}%)\n"

        md_content += "\n## 详细结果\n\n"

        for result in summary['detailed_results']:
            if result['success'] and not result.get('skipped', False):
                filename = Path(result['file']).name
                confidence = result.get('overall_confidence', 0)
                mbti = result.get('representative_mbti', 'N/A')
                agreement = result.get('agreement_level', 'N/A')
                models = f"{len(result.get('successful_models', []))}/{result.get('total_models_attempted', 0)}"

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
        md_file = output_dir / "batch_four_model_report.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='四模型批量云评估Big5分析')
    parser.add_argument('input_path', help='输入文件或目录路径')
    parser.add_argument('--output', default='four_model_results', help='输出目录')
    parser.add_argument('--sample', type=int, help='采样文件数量')
    parser.add_argument('--filter', help='文件名过滤模式')
    parser.add_argument('--delay', type=int, default=20, help='文件间延迟秒数（四模型分析需要更长延迟）')
    parser.add_argument('--resume', action='store_true', help='强制从断点继续（默认自动检测）')

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

    print(f"🔍 找到 {len(input_files)} 个文件进行四模型分析")

    # 创建三模型批量分析器（暂时移除有问题的Claude API）
    analyzer = BatchFourModelAnalyzer(
        models=["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
    )

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 执行批量分析
    def progress_callback(completed, total, result):
        success_rate = sum(1 for r in analyzer.results if r.get('success', False)) / len(analyzer.results) * 100 if analyzer.results else 0
        confidences = [r.get('confidence_analysis', {}).get('overall_confidence', 0) for r in analyzer.results if r.get('success', False)]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        completed_in_batch = len(analyzer.completed_files) + len(analyzer.failed_files)
        print(f"📈 总进度: {completed_in_batch}/{total} ({completed_in_batch/total*100:.1f}%) - 成功率: {success_rate:.1f}% - 平均置信度: {avg_confidence:.1f}%")

    results = analyzer.analyze_batch(
        input_files,
        output_dir,
        progress_callback=progress_callback,
        delay_between_files=args.delay
    )

    # 生成汇总报告
    print(f"\n📋 生成四模型汇总报告...")
    analyzer.generate_summary_report(results, output_dir)

    # 最终统计
    successful = sum(1 for r in results if r['success'] and not r.get('skipped', False))
    skipped = sum(1 for r in results if r.get('skipped', False))
    avg_confidence = sum(r.get('overall_confidence', 0) for r in results if r['success'] and not r.get('skipped', False)) / len([r for r in results if r['success'] and not r.get('skipped', False)]) if successful > 0 else 0
    high_confidence = sum(1 for r in results if r['success'] and not r.get('skipped', False) and r.get('overall_confidence', 0) >= 80)

    print(f"\n🎉 四模型批量分析完成!")
    print(f"✅ 成功: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    if skipped > 0:
        print(f"⏭️  跳过: {skipped} 个文件（断点继续）")
    print(f"📊 平均置信度: {avg_confidence:.1f}%")
    print(f"🎯 高置信度文件: {high_confidence} 个")
    print(f"📁 结果保存在: {output_dir}")
    print(f"🤖 使用模型: {', '.join(analyzer.models)}")
    print(f"🔄 断点文件: {analyzer.progress_file}")

if __name__ == "__main__":
    main()