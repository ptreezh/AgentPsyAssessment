#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端自适应共识算法测试
验证完整的评估流水线集成效果
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'production_pipelines', 'local_batch_production', 'single_report_pipeline'))

def create_test_data():
    """创建测试数据"""

    # 模拟有争议的评估数据
    test_scenarios = [
        {
            "name": "轻微分歧测试",
            "question_id": "TEST_E1",
            "question_data": {
                "dimension": "E",
                "mapped_ipip_concept": "E1: 我是团队活动的核心人物"
            },
            "extracted_response": "我在团队中确实扮演核心角色，经常组织活动",
            "expected_scores": [3, 3, 5]  # 轻微分歧
        },
        {
            "name": "严重分歧测试",
            "question_id": "TEST_A1",
            "question_data": {
                "dimension": "A",
                "mapped_ipip_concept": "A1: 我对他⼈表示同情"
            },
            "extracted_response": "我对他人不太会表达同情",
            "expected_scores": [1, 1, 5]  # 严重分歧
        },
        {
            "name": "完全共识测试",
            "question_id": "TEST_C1",
            "question_data": {
                "dimension": "C",
                "mapped_ipip_concept": "C1: 我做事总是有条不紊"
            },
            "extracted_response": "我确实做事很有条理",
            "expected_scores": [5, 5, 5]  # 完全共识
        }
    ]

    return test_scenarios

def run_adaptive_consensus_test():
    """运行自适应共识算法测试"""

    print("🧠 端到端自适应共识算法测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # 导入透明流水线
        from transparent_pipeline import TransparentPipeline
        from adaptive_consensus_algorithm import AdaptiveConsensusAlgorithm

        print("✅ 成功导入透明流水线和自适应共识算法")
        print()

        # 初始化流水线
        pipeline = TransparentPipeline(use_cloud=True)
        algorithm = AdaptiveConsensusAlgorithm()

        print("✅ 流水线初始化成功")
        print(f"   - 云端模型: {pipeline.primary_models}")
        print(f"   - 争议模型: {pipeline.dispute_models}")
        print(f"   - 最大争议轮数: {pipeline.max_dispute_rounds}")
        print(f"   - 争议阈值: {pipeline.dispute_threshold}")
        print()

        # 获取测试数据
        test_scenarios = create_test_data()

        results = []

        for i, scenario in enumerate(test_scenarios):
            print(f"🔍 测试场景 {i+1}: {scenario['name']}")
            print(f"   题目ID: {scenario['question_id']}")
            print(f"   维度: {scenario['question_data']['dimension']}")
            print(f"   概念: {scenario['question_data']['mapped_ipip_concept']}")
            print(f"   期望评分: {scenario['expected_scores']}")
            print()

            try:
                start_time = time.time()

                # 运行流水线处理
                result = pipeline.process_single_question(scenario, i)

                end_time = time.time()
                processing_time = end_time - start_time

                print("✅ 处理成功")
                print(f"   处理时间: {processing_time:.2f}秒")
                print(f"   最终评分: {result.get('final_adjusted_scores', {})}")
                print(f"   整体可靠性: {result.get('confidence_metrics', {}).get('overall_reliability', 0):.3f}")

                # 检查共识方法
                confidence_metrics = result.get('confidence_metrics', {})
                if 'consensus_method' in confidence_metrics:
                    print(f"   共识方法: {confidence_metrics['consensus_method']}")
                    print(f"   质量指标: {confidence_metrics.get('quality_metrics', {})}")

                print(f"   使用模型: {len(result.get('models_used', []))} 个")
                print(f"   争议轮数: {result.get('resolution_rounds', 0)}")
                print(f"   初始争议: {result.get('disputes_initial', 0)}")
                print(f"   最终争议: {result.get('disputes_final', 0)}")

                results.append({
                    'scenario': scenario['name'],
                    'success': True,
                    'result': result,
                    'processing_time': processing_time
                })

            except Exception as e:
                print(f"❌ 处理失败: {e}")
                import traceback
                traceback.print_exc()

                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'error': str(e),
                    'processing_time': 0
                })

            print("-" * 60)

        # 生成测试报告
        generate_test_report(results)

        return results

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_test_report(results):
    """生成测试报告"""

    print("\n" + "=" * 80)
    print("📊 端到端测试报告")
    print("=" * 80)

    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests

    print(f"总测试数: {total_tests}")
    print(f"成功测试: {successful_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
    print()

    if successful_tests > 0:
        successful_results = [r for r in results if r['success']]

        # 统计处理时间
        avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
        print(f"平均处理时间: {avg_time:.2f}秒")

        # 统计可靠性
        reliabilities = []
        consensus_methods = []
        resolution_rounds = []

        for result in successful_results:
            metrics = result['result'].get('confidence_metrics', {})
            reliabilities.append(metrics.get('overall_reliability', 0))

            if 'consensus_method' in metrics:
                consensus_methods.append(metrics['consensus_method'])

            resolution_rounds.append(result['result'].get('resolution_rounds', 0))

        if reliabilities:
            avg_reliability = sum(reliabilities) / len(reliabilities)
            print(f"平均可靠性: {avg_reliability:.3f}")
            print(f"可靠性范围: {min(reliabilities):.3f} - {max(reliabilities):.3f}")

        if consensus_methods:
            method_counts = {}
            for method in consensus_methods:
                method_counts[method] = method_counts.get(method, 0) + 1
            print(f"共识方法分布: {method_counts}")

        if resolution_rounds:
            avg_rounds = sum(resolution_rounds) / len(resolution_rounds)
            print(f"平均解决轮数: {avg_rounds:.1f}")

        print()

        # 详细结果
        print("📋 详细测试结果:")
        for result in successful_results:
            print(f"  ✅ {result['scenario']}")
            print(f"     可靠性: {result['result'].get('confidence_metrics', {}).get('overall_reliability', 0):.3f}")
            print(f"     处理时间: {result['processing_time']:.2f}秒")
            print(f"     共识方法: {result['result'].get('confidence_metrics', {}).get('consensus_method', 'N/A')}")

    if failed_tests > 0:
        print("\n❌ 失败的测试:")
        for result in results:
            if not result['success']:
                print(f"  ❌ {result['scenario']}: {result.get('error', 'Unknown error')}")

    # 保存报告
    save_test_report(results)

def save_test_report(results):
    """保存测试报告到文件"""

    report_data = {
        'test_time': datetime.now().isoformat(),
        'total_tests': len(results),
        'successful_tests': sum(1 for r in results if r['success']),
        'failed_tests': len(results) - sum(1 for r in results if r['success']),
        'results': results
    }

    # 创建输出目录
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)

    # 保存报告
    report_file = os.path.join(output_dir, f'adaptive_consensus_test_report_{int(time.time())}.json')

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"\n📁 测试报告已保存到: {report_file}")

    except Exception as e:
        print(f"\n❌ 保存报告失败: {e}")

if __name__ == "__main__":
    print("🚀 开始端到端自适应共识算法测试")

    results = run_adaptive_consensus_test()

    if results and any(r['success'] for r in results):
        print("\n🎉 端到端测试完成！自适应共识算法集成验证成功")
        sys.exit(0)
    else:
        print("\n❌ 端到端测试失败，请检查系统配置")
        sys.exit(1)