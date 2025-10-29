#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据质量增强评估器 - 设置90%最低成功率阈值
"""

import json
import os
import sys
import subprocess
import threading
import time
import statistics
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional

class DataQualityEnhancedEvaluator:
    def __init__(self, min_success_rate=0.9):
        """
        初始化数据质量增强评估器

        Args:
            min_success_rate: 最低成功率阈值，默认90%
        """
        self.min_success_rate = min_success_rate
        self.quality_metrics = {
            'total_evaluations': 0,
            'passed_quality_threshold': 0,
            'failed_quality_threshold': 0,
            'average_success_rate': 0.0,
            'quality_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }

    def calculate_quality_score(self, success_rate: float, consistency_score: float = 0) -> float:
        """
        计算数据质量分数

        Args:
            success_rate: 实际成功率 (0-1)
            consistency_score: 一致性分数 (0-100)

        Returns:
            质量分数 (0-100)
        """
        # 成功率权重70%，一致性权重30%
        quality_score = (success_rate * 70) + (consistency_score * 0.3)
        return round(quality_score, 1)

    def meets_quality_threshold(self, success_rate: float) -> bool:
        """
        检查是否满足质量阈值

        Args:
            success_rate: 成功率 (0-1)

        Returns:
            是否满足质量要求
        """
        return success_rate >= self.min_success_rate

    def evaluate_data_quality(self, results: Dict) -> Dict:
        """
        评估数据质量

        Args:
            results: 评估结果

        Returns:
            质量评估结果
        """
        quality_assessment = {
            'meets_threshold': False,
            'success_rate': 0.0,
            'quality_score': 0.0,
            'quality_level': 'low',
            'recommendations': [],
            'detailed_analysis': {}
        }

        # 计算成功率
        if 'model_results' in results:
            total_segments = 0
            successful_segments = 0

            for model_name, model_result in results['model_results'].items():
                if 'success_rate' in model_result:
                    total_segments += 1
                    successful_segments += model_result['success_rate']

            if total_segments > 0:
                avg_success_rate = successful_segments / total_segments
                quality_assessment['success_rate'] = avg_success_rate
                quality_assessment['meets_threshold'] = self.meets_quality_threshold(avg_success_rate)

                # 计算一致性分数
                consistency_score = results.get('consistency_analysis', {}).get('confidence_score', 0)
                quality_assessment['quality_score'] = self.calculate_quality_score(avg_success_rate, consistency_score)

                # 确定质量等级
                if avg_success_rate >= 0.95:
                    quality_assessment['quality_level'] = 'high'
                elif avg_success_rate >= 0.9:
                    quality_assessment['quality_level'] = 'medium'
                else:
                    quality_assessment['quality_level'] = 'low'

                # 生成建议
                if avg_success_rate < 0.9:
                    quality_assessment['recommendations'].append("成功率低于90%，建议重新评估")
                if avg_success_rate < 0.7:
                    quality_assessment['recommendations'].append("成功率过低，结果不可信")
                if consistency_score < 50:
                    quality_assessment['recommendations'].append("模型一致性不足")

                quality_assessment['detailed_analysis'] = {
                    'total_models_evaluated': total_segments,
                    'segments_analyzed': results.get('total_segments', 0),
                    'quality_threshold_met': quality_assessment['meets_threshold'],
                    'gap_to_threshold': max(0, self.min_success_rate - avg_success_rate)
                }

        return quality_assessment

class EnhancedOllamaEvaluator(DataQualityEnhancedEvaluator):
    def __init__(self, models: List[str], min_success_rate=0.9):
        super().__init__(min_success_rate)
        self.models = models
        self.olllama_base = "http://localhost:11434"

    def analyze_with_quality_control(self, input_file: str, output_dir: str) -> Dict:
        """
        带质量控制的分析

        Args:
            input_file: 输入文件路径
            output_dir: 输出目录

        Returns:
            分析结果
        """
        print(f"🔍 开始质量控制分析: {os.path.basename(input_file)}")

        # 首先进行标准分析
        standard_result = self._standard_analysis(input_file, output_dir)

        # 然后进行质量评估
        quality_assessment = self.evaluate_data_quality(standard_result)

        # 更新质量统计
        self.quality_metrics['total_evaluations'] += 1
        self.quality_metrics['average_success_rate'] = (
            (self.quality_metrics['average_success_rate'] * (self.quality_metrics['total_evaluations'] - 1) +
             quality_assessment['success_rate']) / self.quality_metrics['total_evaluations']
        )

        if quality_assessment['meets_threshold']:
            self.quality_metrics['passed_quality_threshold'] += 1
            self.quality_metrics['quality_distribution'][quality_assessment['quality_level']] += 1
        else:
            self.quality_metrics['failed_quality_threshold'] += 1

        # 添加质量信息到结果中
        enhanced_result = {
            **standard_result,
            'quality_assessment': quality_assessment,
            'meets_minimum_quality': quality_assessment['meets_threshold'],
            'quality_score': quality_assessment['quality_score'],
            'analysis_timestamp': datetime.now().isoformat()
        }

        # 保存增强结果
        output_filename = input_file.replace('.json', '_quality_enhanced_analysis.json')
        output_path = os.path.join(output_dir, os.path.basename(output_filename))

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_result, f, ensure_ascii=False, indent=2)

        print(f"   📊 成功率: {quality_assessment['success_rate']:.1%}")
        print(f"   🎯 质量分数: {quality_assessment['quality_score']}")
        print(f"   {'✅' if quality_assessment['meets_threshold'] else '❌'} 质量阈值: {'通过' if quality_assessment['meets_threshold'] else '未通过'}")

        return enhanced_result

    def _standard_analysis(self, input_file: str, output_dir: str) -> Dict:
        """标准分析流程（简化版，实际会调用原有的分析逻辑）"""
        # 这里会调用原有的三模型分析逻辑
        # 为了演示，返回模拟结果
        return {
            'source_file': os.path.basename(input_file),
            'model_results': {
                'deepseek-v3.1:671b-cloud': {'success_rate': 0.85},
                'gpt-oss:20b-cloud': {'success_rate': 0.92},
                'qwen3-coder:480b-cloud': {'success_rate': 0.78}
            },
            'consistency_analysis': {
                'confidence_score': 75,
                'consensus_mbti': 'ISTJ'
            },
            'total_segments': 10
        }

class QualityControlReport:
    def __init__(self):
        self.report_data = {
            'generation_time': datetime.now().isoformat(),
            'quality_threshold': 0.9,
            'evaluators': {},
            'summary': {},
            'recommendations': []
        }

    def generate_report(self, ollama_metrics: Dict, cloud_metrics: Dict, output_path: str):
        """生成质量控制报告"""

        self.report_data['evaluators']['ollama'] = ollama_metrics
        self.report_data['evaluators']['cloud'] = cloud_metrics

        # 计算总体统计
        total_evaluations = ollama_metrics['total_evaluations'] + cloud_metrics['total_evaluations']
        total_passed = ollama_metrics['passed_quality_threshold'] + cloud_metrics['passed_quality_threshold']

        self.report_data['summary'] = {
            'total_evaluations': total_evaluations,
            'passed_quality_threshold': total_passed,
            'failed_quality_threshold': total_evaluations - total_passed,
            'overall_pass_rate': (total_passed / total_evaluations * 100) if total_evaluations > 0 else 0,
            'quality_threshold_percentage': 90
        }

        # 生成建议
        if self.report_data['summary']['overall_pass_rate'] < 50:
            self.report_data['recommendations'].extend([
                "系统整体质量不达标，建议检查模型可用性",
                "考虑降低并发数量，提高单个请求的成功率",
                "增加重试机制和错误恢复策略"
            ])

        if self.report_data['summary']['overall_pass_rate'] < 80:
            self.report_data['recommendations'].extend([
                "建议优化网络连接和API调用稳定性",
                "考虑实施更严格的超时控制"
            ])

        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, ensure_ascii=False, indent=2)

        return output_path

def create_quality_control_patch():
    """创建质量控制补丁，修改现有评估器"""

    patch_content = '''
# 数据质量增强补丁
# 添加到 three_model_ollama_evaluator.py

def apply_quality_control_enhancement(self):
    """应用质量控制增强"""
    self.min_success_rate = 0.9  # 90%最低成功率
    self.quality_stats = {
        'total_analyzed': 0,
        'passed_quality': 0,
        'failed_quality': 0
    }

def check_data_quality(self, model_results):
    """检查数据质量"""
    success_rates = []
    for model, result in model_results.items():
        if 'success_rate' in result:
            success_rates.append(result['success_rate'])

    if not success_rates:
        return False, 0.0

    avg_success_rate = sum(success_rates) / len(success_rates)
    meets_threshold = avg_success_rate >= self.min_success_rate

    return meets_threshold, avg_success_rate

def enhance_result_with_quality(self, result):
    """增强结果包含质量信息"""
    if 'model_results' in result:
        meets_threshold, success_rate = self.check_data_quality(result['model_results'])

        result['quality_assessment'] = {
            'meets_90_percent_threshold': meets_threshold,
            'average_success_rate': success_rate,
            'quality_score': success_rate * 100,
            'timestamp': datetime.now().isoformat()
        }

        # 更新质量统计
        self.quality_stats['total_analyzed'] += 1
        if meets_threshold:
            self.quality_stats['passed_quality'] += 1
        else:
            self.quality_stats['failed_quality'] += 1

    return result
'''

    with open('quality_control_patch.py', 'w', encoding='utf-8') as f:
        f.write(patch_content)

    print("✅ 质量控制补丁已创建: quality_control_patch.py")

def main():
    """主函数 - 演示质量控制增强"""
    print("🔧 数据质量增强评估器")
    print("=" * 80)
    print("设置90%最低成功率阈值")

    # 创建质量控制补丁
    create_quality_control_patch()

    # 演示质量增强评估器
    models = ['deepseek-v3.1:671b-cloud', 'gpt-oss:20b-cloud', 'qwen3-coder:480b-cloud']
    enhanced_evaluator = EnhancedOllamaEvaluator(models, min_success_rate=0.9)

    print("\n📊 质量控制配置:")
    print(f"   最低成功率阈值: {enhanced_evaluator.min_success_rate:.0%}")
    print(f"   质量评分权重: 成功率70% + 一致性30%")

    print("\n🎯 质量等级定义:")
    print("   高质量: 成功率 ≥ 95%")
    print("   中等质量: 90% ≤ 成功率 < 95%")
    print("   低质量: 成功率 < 90% (不满足最低要求)")

    print("\n📋 实施建议:")
    print("1. 在现有评估器中应用质量控制补丁")
    print("2. 所有低于90%成功率的结果标记为'不可信'")
    print("3. 生成质量报告，追踪系统整体质量")
    print("4. 根据质量统计优化模型调用策略")

    # 生成质量控制配置文件
    config = {
        'quality_control': {
            'min_success_rate': 0.9,
            'quality_weights': {'success_rate': 0.7, 'consistency': 0.3},
            'quality_levels': {
                'high': {'min_rate': 0.95, 'label': '高质量'},
                'medium': {'min_rate': 0.9, 'label': '中等质量'},
                'low': {'max_rate': 0.9, 'label': '低质量'}
            },
            'action_rules': {
                'below_threshold': '标记为不可信，建议重新评估',
                'warning_threshold': 0.85,
                'critical_threshold': 0.7
            }
        }
    }

    with open('quality_control_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\n✅ 质量控制配置已保存: quality_control_config.json")
    print("🔧 质量控制补丁已生成: quality_control_patch.py")

if __name__ == "__main__":
    main()