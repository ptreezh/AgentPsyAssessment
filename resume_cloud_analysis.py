#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云评估器分析恢复脚本
用于恢复中断的批量分析任务，支持断点续传
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from cloud_segmented_analysis import CloudSegmentedPersonalityAnalyzer

class ResumeCloudAnalysis:
    """云评估器分析恢复器"""

    def __init__(self, model: str = "qwen-long", api_key: str = None):
        self.model = model
        self.api_key = api_key or "sk-ffd03518254b495b8d27e723cd413fc1"
        self.completed_files = set()
        self.failed_files = []

    def load_completed_files(self, output_dir: Path):
        """加载已完成的文件列表"""
        output_dir = Path(output_dir) / self.model
        if not output_dir.exists():
            return

        for file_path in output_dir.glob("*_segmented.json"):
            # 提取原始文件名
            original_name = file_path.name.replace(f"_{self.model}_segmented.json", "")
            self.completed_files.add(original_name)

        print(f"📂 发现 {len(self.completed_files)} 个已完成的分析文件")

    def get_remaining_files(self, input_dir: Path) -> list[Path]:
        """获取待分析的文件列表"""
        all_files = list(input_dir.glob("*.json"))
        remaining_files = []

        for file_path in all_files:
            if file_path.name not in self.completed_files:
                remaining_files.append(file_path)

        return remaining_files

    def analyze_single_file(self, input_file: Path, output_dir: Path, max_retries: int = 3) -> dict:
        """分析单个文件，支持重试机制"""
        for attempt in range(max_retries):
            try:
                print(f"🔍 [{attempt+1}/{max_retries}] 开始分析: {input_file.name}")

                # 创建分析器
                analyzer = CloudSegmentedPersonalityAnalyzer(
                    model=self.model,
                    api_key=self.api_key
                )

                # 执行分析
                result = analyzer.analyze_full_assessment(str(input_file))

                # 保存结果
                output_file = output_dir / self.model / f"{input_file.stem}_{self.model}_segmented.json"
                output_file.parent.mkdir(parents=True, exist_ok=True)

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

                return summary

            except Exception as e:
                print(f"❌ 尝试 {attempt+1} 失败: {input_file.name} - {e}")

                if attempt < max_retries - 1:
                    # 指数退避
                    wait_time = 5 * (2 ** attempt)
                    print(f"   等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"   最终失败: {input_file.name}")
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
                    self.failed_files.append(error_summary)
                    return error_summary

    def resume_analysis(self, input_dir: Path, output_dir: Path,
                       max_files: int = None, delay_between_files: int = 3):
        """恢复分析任务"""
        print(f"🚀 恢复云评估器分析任务")
        print(f"📂 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {self.model}")

        # 加载已完成文件
        self.load_completed_files(output_dir)

        # 获取剩余文件
        remaining_files = self.get_remaining_files(input_dir)

        if max_files:
            remaining_files = remaining_files[:max_files]

        if not remaining_files:
            print("✅ 所有文件已完成分析")
            return

        print(f"📊 剩余待分析文件: {len(remaining_files)}")

        results = []
        completed = 0

        for i, input_file in enumerate(remaining_files, 1):
            print(f"\n📈 进度: {i}/{len(remaining_files)} ({i/len(remaining_files)*100:.1f}%)")

            # 分析文件
            result = self.analyze_single_file(input_file, output_dir)
            results.append(result)

            if result['success']:
                completed += 1

            # 添加延迟避免API限制
            if i < len(remaining_files):
                print(f"⏱️  等待 {delay_between_files} 秒...")
                time.sleep(delay_between_files)

        # 生成汇总报告
        self.generate_summary_report(results, output_dir)

        # 最终统计
        successful = sum(1 for r in results if r['success'])
        print(f"\n🎉 恢复分析完成!")
        print(f"✅ 本次成功: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
        print(f"📁 失败文件: {len(self.failed_files)}")
        print(f"📂 总计完成: {len(self.completed_files) + completed}")

    def generate_summary_report(self, results: list[dict], output_dir: Path):
        """生成汇总报告"""
        successful_results = [r for r in results if r['success']]

        if not successful_results:
            print("⚠️  没有成功的分析结果，跳过汇总报告生成")
            return

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
                'total_files_analyzed': len(results),
                'successful': len(successful_results),
                'failed': len(self.failed_files),
                'success_rate': len(successful_results) / len(results) * 100 if results else 0,
                'model_used': self.model,
                'analysis_timestamp': datetime.now().isoformat(),
                'previously_completed': len(self.completed_files)
            },
            'big5_distribution': big5_stats,
            'mbti_distribution': mbti_stats,
            'detailed_results': results,
            'failed_files': self.failed_files
        }

        # 保存JSON汇总
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        json_summary = output_path / f"resume_summary_{self.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_summary, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"📊 汇总报告已保存: {json_summary}")

        # 显示简要统计
        print(f"\n📋 本次分析统计:")
        print(f"📊 Big5评分分布:")
        for trait, scores in big5_stats.items():
            total = sum(scores.values())
            print(f"  {trait.replace('_', ' ').title()}: 1分({scores[1]}/{total}) 3分({scores[3]}/{total}) 5分({scores[5]}/{total})")

        print(f"\n🧠 MBTI类型分布:")
        for mbti_type, count in sorted(mbti_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {mbti_type}: {count}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='恢复云评估器分析任务')
    parser.add_argument('input_dir', default='results/results', help='输入目录路径')
    parser.add_argument('--output', default='batch_cloud_segmented_results', help='输出目录')
    parser.add_argument('--model', default='qwen-long', choices=['qwen-long', 'qwen-max'],
                       help='使用的云模型')
    parser.add_argument('--max-files', type=int, help='最大处理文件数')
    parser.add_argument('--delay', type=int, default=3, help='文件间延迟秒数')

    args = parser.parse_args()

    # 创建恢复分析器
    analyzer = ResumeCloudAnalysis(model=args.model)

    # 执行恢复分析
    analyzer.resume_analysis(
        Path(args.input_dir),
        Path(args.output),
        max_files=args.max_files,
        delay_between_files=args.delay
    )

if __name__ == "__main__":
    main()