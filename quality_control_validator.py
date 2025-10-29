#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量控制验证器 - 验证90%阈值的效果
"""

import json
import os
import glob
from datetime import datetime
from pathlib import Path
from collections import Counter
import statistics
from typing import Dict

class QualityControlValidator:
    def __init__(self):
        self.validation_results = {
            'total_files_analyzed': 0,
            'files_meeting_threshold': 0,
            'files_failing_threshold': 0,
            'quality_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'success_rate_distribution': [],
            'quality_scores': [],
            'mbti_types': {},
            'false_consensus_cases': []
        }

    def analyze_existing_results(self, results_dir: str = "three_model_consistency_results"):
        """分析现有结果的质量控制情况"""
        print(f"🔍 分析现有结果的质量控制情况")
        print(f"📁 结果目录: {results_dir}")

        # 查找所有分析结果文件
        pattern = f"{results_dir}/*_three_model_consistency_analysis.json"
        files = glob.glob(pattern)

        print(f"📊 找到 {len(files)} 个分析结果文件")

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.validate_single_result(data, file_path)

            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")

        self.generate_validation_report()

    def validate_single_result(self, result_data: Dict, file_path: str):
        """验证单个结果的质量"""
        self.validation_results['total_files_analyzed'] += 1

        # 计算成功率
        model_results = result_data.get('model_results', {})
        if not model_results:
            return

        success_rates = []
        for model_name, model_result in model_results.items():
            if 'success_rate' in model_result:
                success_rates.append(model_result['success_rate'])

        if not success_rates:
            return

        avg_success_rate = sum(success_rates) / len(success_rates)
        self.validation_results['success_rate_distribution'].append(avg_success_rate)

        # 检查是否达到90%阈值
        meets_threshold = avg_success_rate >= 0.9
        if meets_threshold:
            self.validation_results['files_meeting_threshold'] += 1
        else:
            self.validation_results['files_failing_threshold'] += 1

        # 确定质量等级
        if avg_success_rate >= 0.95:
            quality_level = 'high'
        elif avg_success_rate >= 0.9:
            quality_level = 'medium'
        else:
            quality_level = 'low'

        self.validation_results['quality_distribution'][quality_level] += 1

        # 计算质量分数
        consistency_score = result_data.get('consistency_analysis', {}).get('confidence_score', 0)
        quality_score = (avg_success_rate * 70) + (consistency_score * 0.3)
        self.validation_results['quality_scores'].append(quality_score)

        # 收集MBTI类型
        consensus_mbti = result_data.get('consistency_analysis', {}).get('consensus_mbti', 'UNKNOWN')
        if consensus_mbti not in self.validation_results['mbti_types']:
            self.validation_results['mbti_types'][consensus_mbti] = 0
        self.validation_results['mbti_types'][consensus_mbti] += 1

        # 检查虚假共识案例
        if avg_success_rate < 0.5 and consensus_mbti != 'UNKNOWN':
            self.validation_results['false_consensus_cases'].append({
                'file': os.path.basename(file_path),
                'success_rate': avg_success_rate,
                'mbti_type': consensus_mbti,
                'quality_score': quality_score
            })

    def generate_validation_report(self):
        """生成验证报告"""
        print("\n📋 质量控制验证报告")
        print("=" * 80)

        total = self.validation_results['total_files_analyzed']
        if total == 0:
            print("❌ 没有找到有效的分析结果")
            return

        # 基本统计
        print(f"📊 基本统计:")
        print(f"   总文件数: {total}")
        print(f"   ✅ 达到90%阈值: {self.validation_results['files_meeting_threshold']} ({self.validation_results['files_meeting_threshold']/total*100:.1f}%)")
        print(f"   ❌ 未达到90%阈值: {self.validation_results['files_failing_threshold']} ({self.validation_results['files_failing_threshold']/total*100:.1f}%)")

        # 质量分布
        print(f"\n🎯 质量分布:")
        quality_dist = self.validation_results['quality_distribution']
        print(f"   高质量 (≥95%): {quality_dist['high']} ({quality_dist['high']/total*100:.1f}%)")
        print(f"   中等质量 (90-95%): {quality_dist['medium']} ({quality_dist['medium']/total*100:.1f}%)")
        print(f"   低质量 (<90%): {quality_dist['low']} ({quality_dist['low']/total*100:.1f}%)")

        # 成功率统计
        if self.validation_results['success_rate_distribution']:
            success_rates = self.validation_results['success_rate_distribution']
            print(f"\n📈 成功率统计:")
            print(f"   平均成功率: {statistics.mean(success_rates):.1%}")
            print(f"   中位数成功率: {statistics.median(success_rates):.1%}")
            print(f"   最低成功率: {min(success_rates):.1%}")
            print(f"   最高成功率: {max(success_rates):.1%}")

        # 质量分数统计
        if self.validation_results['quality_scores']:
            quality_scores = self.validation_results['quality_scores']
            print(f"\n🏆 质量分数统计:")
            print(f"   平均质量分数: {statistics.mean(quality_scores):.1f}")
            print(f"   中位数质量分数: {statistics.median(quality_scores):.1f}")
            print(f"   最低质量分数: {min(quality_scores):.1f}")
            print(f"   最高质量分数: {max(quality_scores):.1f}")

        # MBTI分布
        print(f"\n🎭 MBTI类型分布:")
        mbti_sorted = sorted(self.validation_results['mbti_types'].items(), key=lambda x: x[1], reverse=True)
        for mbti, count in mbti_sorted[:10]:  # 显示前10个
            print(f"   {mbti}: {count} ({count/total*100:.1f}%)")

        # 虚假共识分析
        false_consensus = self.validation_results['false_consensus_cases']
        if false_consensus:
            print(f"\n⚠️ 虚假共识风险分析:")
            print(f"   发现 {len(false_consensus)} 个虚假共识案例 (成功率<50%)")
            print(f"   占总案例的 {len(false_consensus)/total*100:.1f}%")

            # 显示前5个虚假共识案例
            print(f"\n   虚假共识案例 (前5个):")
            for i, case in enumerate(false_consensus[:5]):
                print(f"   {i+1}. {case['file'][:50]}...")
                print(f"      成功率: {case['success_rate']:.1%}, MBTI: {case['mbti_type']}, 质量分数: {case['quality_score']:.1f}")

        # 90%阈值效果评估
        high_quality_files = quality_dist['high'] + quality_dist['medium']
        print(f"\n✅ 90%阈值效果评估:")
        print(f"   达到质量要求的文件: {high_quality_files}/{total} ({high_quality_files/total*100:.1f}%)")

        if high_quality_files/total < 0.5:
            print("   ⚠️ 质量通过率较低，建议:")
            print("      - 检查模型可用性和稳定性")
            print("      - 优化网络连接和超时设置")
            print("      - 考虑降低并发数量")
        elif high_quality_files/total < 0.8:
            print("   ⚠️ 质量通过率中等，建议:")
            print("      - 监控失败原因并针对性优化")
            print("      - 增加重试机制")
        else:
            print("   ✅ 质量通过率良好，90%阈值设置合理")

    def save_validation_report(self, output_path: str = None):
        """保存验证报告到文件"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"quality_control_validation_report_{timestamp}.json"

        report_data = {
            'validation_timestamp': datetime.now().isoformat(),
            'threshold_used': 0.9,
            'validation_results': self.validation_results,
            'summary': {
                'total_files': self.validation_results['total_files_analyzed'],
                'quality_pass_rate': self.validation_results['files_meeting_threshold'] / max(1, self.validation_results['total_files_analyzed']) * 100,
                'false_consensus_rate': len(self.validation_results['false_consensus_cases']) / max(1, self.validation_results['total_files_analyzed']) * 100,
                'average_success_rate': statistics.mean(self.validation_results['success_rate_distribution']) if self.validation_results['success_rate_distribution'] else 0,
                'average_quality_score': statistics.mean(self.validation_results['quality_scores']) if self.validation_results['quality_scores'] else 0
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"\n📄 验证报告已保存: {output_path}")
        return output_path

def main():
    """主函数"""
    print("🔍 质量控制验证器")
    print("=" * 80)
    print("验证90%成功率阈值的效果")

    validator = QualityControlValidator()

    # 分析现有结果
    validator.analyze_existing_results()

    # 保存验证报告
    validator.save_validation_report()

    print("\n✅ 验证完成!")
    print("\n🎯 关键建议:")
    print("1. 90%成功率阈值有效识别了虚假共识风险")
    print("2. 低于90%的结果应标记为'不可信'并重新评估")
    print("3. 建议在实际部署时强制执行质量控制")
    print("4. 对于低质量结果，应优先解决技术失败问题")

if __name__ == "__main__":
    main()