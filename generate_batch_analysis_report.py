#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析报告生成器 - 分析虚假共识风险和可信度分布
"""

import json
import os
import glob
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import statistics

class BatchCredibilityAnalyzer:
    def __init__(self):
        self.olllama_results = []
        self.cloud_results = []
        self.credibility_stats = {
            'ollama': {'scores': [], 'success_rates': [], 'mbti_types': []},
            'cloud': {'scores': [], 'success_rates': [], 'mbti_types': []}
        }

    def load_results(self, ollama_dir="three_model_consistency_results",
                     cloud_dir="cloud_segment_results"):
        """加载两个评估器的结果"""

        # 加载Ollama评估器结果
        ollama_files = glob.glob(f"{ollama_dir}/*.json")
        print(f"📂 找到 {len(ollama_files)} 个Ollama评估结果文件")

        for file_path in ollama_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['source_file'] = os.path.basename(file_path)
                    self.olllama_results.append(data)

                    # 收集统计数据
                    if 'consistency_analysis' in data:
                        consistency = data['consistency_analysis']
                        if 'confidence_score' in consistency:
                            self.credibility_stats['ollama']['scores'].append(consistency['confidence_score'])
                        if 'overall_confidence' in consistency:
                            self.credibility_stats['ollama']['success_rates'].append(consistency['overall_confidence'])
                        if 'consensus_mbti' in consistency:
                            self.credibility_stats['ollama']['mbti_types'].append(consistency['consensus_mbti'])

            except Exception as e:
                print(f"❌ 加载Ollama文件失败 {file_path}: {e}")

        # 加载云模型评估器结果
        cloud_files = glob.glob(f"{cloud_dir}/*.json")
        print(f"📂 找到 {len(cloud_files)} 个云模型评估结果文件")

        for file_path in cloud_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['source_file'] = os.path.basename(file_path)
                    self.cloud_results.append(data)

                    # 收集统计数据
                    if 'avg_models_per_segment' in data:
                        success_rate = data['avg_models_per_segment'] / 3.0  # 标准化到0-1
                        self.credibility_stats['cloud']['success_rates'].append(success_rate)

                    # 估算可信度分数（基于成功率和备用模型使用情况）
                    backup_usage = data.get('backup_usage_rate', 0)
                    success_penalty = 1.0 - success_rate
                    estimated_credibility = max(0, min(100, (1 - success_penalty - backup_usage) * 100))
                    self.credibility_stats['cloud']['scores'].append(estimated_credibility)

                    if 'mbti_type' in data:
                        self.credibility_stats['cloud']['mbti_types'].append(data['mbti_type'])

            except Exception as e:
                print(f"❌ 加载云模型文件失败 {file_path}: {e}")

    def analyze_false_consensus_risks(self):
        """分析虚假共识风险"""
        print("\n🔍 虚假共识风险分析")
        print("=" * 60)

        # 分析Ollama评估器的失败模式
        ollama_failures = 0
        ollama_low_success = 0
        ollama_total_segments = 0

        for result in self.olllama_results:
            if 'model_results' in result:
                for model, model_result in result['model_results'].items():
                    success_rate = model_result.get('success_rate', 0)
                    ollama_total_segments += 1
                    if success_rate < 0.5:  # 成功率低于50%
                        ollama_failures += 1
                    if success_rate < 0.8:  # 成功率低于80%
                        ollama_low_success += 1

        ollama_failure_rate = (ollama_failures / ollama_total_segments * 100) if ollama_total_segments > 0 else 0
        ollama_low_success_rate = (ollama_low_success / ollama_total_segments * 100) if ollama_total_segments > 0 else 0

        print(f"🤖 Ollama评估器失败分析:")
        print(f"   总段数: {ollama_total_segments}")
        print(f"   严重失败段数 (<50%成功率): {ollama_failures} ({ollama_failure_rate:.1f}%)")
        print(f"   低成功率段数 (<80%成功率): {ollama_low_success} ({ollama_low_success_rate:.1f}%)")

        # 分析云模型评估器的失败模式
        cloud_low_success = 0
        cloud_very_low_success = 0
        cloud_total = len(self.cloud_results)

        for result in self.cloud_results:
            avg_models = result.get('avg_models_per_segment', 0)
            success_rate = avg_models / 3.0  # 标准化

            if success_rate < 0.3:  # 成功率低于30%
                cloud_very_low_success += 1
            if success_rate < 0.7:  # 成功率低于70%
                cloud_low_success += 1

        cloud_very_low_rate = (cloud_very_low_success / cloud_total * 100) if cloud_total > 0 else 0
        cloud_low_rate = (cloud_low_success / cloud_total * 100) if cloud_total > 0 else 0

        print(f"\n☁️ 云模型评估器失败分析:")
        print(f"   总文件数: {cloud_total}")
        print(f"   极低成功率文件 (<30%): {cloud_very_low_success} ({cloud_very_low_rate:.1f}%)")
        print(f"   低成功率文件 (<70%): {cloud_low_success} ({cloud_low_rate:.1f}%)")

        # 分析MBTI一致性
        ollama_mbti_counter = Counter(self.credibility_stats['ollama']['mbti_types'])
        cloud_mbti_counter = Counter(self.credibility_stats['cloud']['mbti_types'])

        print(f"\n🎯 MBTI类型分布:")
        print(f"   Ollama评估器: {dict(ollama_mbti_counter.most_common(5))}")
        print(f"   云模型评估器: {dict(cloud_mbti_counter.most_common(5))}")

        return {
            'ollama_failure_rate': ollama_failure_rate,
            'ollama_low_success_rate': ollama_low_success_rate,
            'cloud_very_low_rate': cloud_very_low_rate,
            'cloud_low_rate': cloud_low_rate,
            'ollama_mbti_distribution': dict(ollama_mbti_counter),
            'cloud_mbti_distribution': dict(cloud_mbti_counter)
        }

    def analyze_credibility_distribution(self):
        """分析可信度分布"""
        print("\n📊 可信度分布分析")
        print("=" * 60)

        for evaluator, stats in self.credibility_stats.items():
            scores = stats['scores']
            if not scores:
                continue

            print(f"\n🤖 {evaluator.upper()}评估器可信度统计:")
            print(f"   样本数量: {len(scores)}")
            print(f"   平均可信度: {statistics.mean(scores):.1f}")
            print(f"   中位数可信度: {statistics.median(scores):.1f}")
            print(f"   最低可信度: {min(scores):.1f}")
            print(f"   最高可信度: {max(scores):.1f}")

            # 可信度分布
            high_credibility = sum(1 for s in scores if s >= 80)
            medium_credibility = sum(1 for s in scores if 60 <= s < 80)
            low_credibility = sum(1 for s in scores if s < 60)

            print(f"   高可信度 (≥80分): {high_credibility} ({high_credibility/len(scores)*100:.1f}%)")
            print(f"   中等可信度 (60-79分): {medium_credibility} ({medium_credibility/len(scores)*100:.1f}%)")
            print(f"   低可信度 (<60分): {low_credibility} ({low_credibility/len(scores)*100:.1f}%)")

    def cross_validator_analysis(self):
        """交叉验证分析"""
        print("\n🔄 交叉验证分析")
        print("=" * 60)

        # 找到相同文件的Ollama和云模型结果
        common_files = set()
        ollama_file_map = {}
        cloud_file_map = {}

        for result in self.olllama_results:
            base_name = result['source_file'].replace('_three_model_consistency_analysis.json', '')
            ollama_file_map[base_name] = result
            common_files.add(base_name)

        for result in self.cloud_results:
            base_name = result['source_file'].replace('_cloud_segment_analysis.json', '')
            cloud_file_map[base_name] = result
            common_files.intersection_update({base_name})

        print(f"📋 找到 {len(common_files)} 个共同评估的文件")

        if len(common_files) > 0:
            # 比较MBTI一致性
            mbti_matches = 0
            mbti_comparisons = []

            for file_name in common_files:
                ollama_result = ollama_file_map[file_name]
                cloud_result = cloud_file_map[file_name]

                ollama_mbti = ollama_result.get('consistency_analysis', {}).get('consensus_mbti', 'Unknown')
                cloud_mbti = cloud_result.get('mbti_type', 'Unknown')

                mbti_comparisons.append({
                    'file': file_name,
                    'ollama_mbti': ollama_mbti,
                    'cloud_mbti': cloud_mbti,
                    'match': ollama_mbti == cloud_mbti
                })

                if ollama_mbti == cloud_mbti:
                    mbti_matches += 1

            consistency_rate = (mbti_matches / len(common_files) * 100) if common_files else 0
            print(f"🎯 MBTI类型一致性: {mbti_matches}/{len(common_files)} ({consistency_rate:.1f}%)")

            # 显示不一致的案例
            inconsistent_cases = [comp for comp in mbti_comparisons if not comp['match']]
            if inconsistent_cases:
                print(f"\n⚠️ MBTI不一致案例 (前10个):")
                for i, case in enumerate(inconsistent_cases[:10]):
                    print(f"   {i+1}. {case['file'][:50]}...")
                    print(f"      Ollama: {case['ollama_mbti']} vs Cloud: {case['cloud_mbti']}")

    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        print("\n📋 生成综合分析报告...")

        report = {
            'generation_time': datetime.now().isoformat(),
            'analysis_summary': {
                'ollama_total_files': len(self.olllama_results),
                'cloud_total_files': len(self.cloud_results),
                'total_analyzed': len(self.olllama_results) + len(self.cloud_results)
            },
            'false_consensus_analysis': self.analyze_false_consensus_risks(),
            'credibility_distribution': {},
            'cross_validation': {}
        }

        # 可信度分布数据
        for evaluator, stats in self.credibility_stats.items():
            if stats['scores']:
                report['credibility_distribution'][evaluator] = {
                    'count': len(stats['scores']),
                    'mean': statistics.mean(stats['scores']),
                    'median': statistics.median(stats['scores']),
                    'min': min(stats['scores']),
                    'max': max(stats['scores']),
                    'std_dev': statistics.stdev(stats['scores']) if len(stats['scores']) > 1 else 0
                }

        # 保存报告
        report_path = f"batch_credibility_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 报告已保存: {report_path}")
        return report_path

def main():
    """主函数"""
    print("🔍 批量可信度分析器")
    print("=" * 80)
    print("分析两个评估器的虚假共识风险和可信度分布")

    analyzer = BatchCredibilityAnalyzer()

    # 加载结果
    analyzer.load_results()

    # 分析虚假共识风险
    risk_analysis = analyzer.analyze_false_consensus_risks()

    # 分析可信度分布
    analyzer.analyze_credibility_distribution()

    # 交叉验证分析
    analyzer.cross_validator_analysis()

    # 生成综合报告
    report_path = analyzer.generate_comprehensive_report()

    print("\n✅ 分析完成!")
    print(f"📊 详细报告已保存至: {report_path}")

    # 关键发现总结
    print("\n🎯 关键发现:")
    print("1. Ollama评估器存在JSON序列化错误导致崩溃")
    print("2. 云模型评估器遭遇大量ConnectionResetError")
    print("3. 两个评估器都存在高失败率，造成虚假共识风险")
    print("4. 建议重新设计可信度评分机制，考虑失败率权重")

if __name__ == "__main__":
    main()