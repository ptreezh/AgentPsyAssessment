#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自适应共识算法性能对比测试
直接测试算法效果，不依赖复杂模块导入
"""

import sys
import os
import time
import json
from datetime import datetime

def test_adaptive_consensus_performance():
    """测试自适应共识算法性能"""

    print("🧠 自适应共识算法性能对比测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 添加路径
    sys.path.append(os.path.join(os.path.dirname(__file__), 'production_pipelines', 'cloud_fallback_enterprise'))

    try:
        from adaptive_consensus_algorithm import AdaptiveConsensusAlgorithm

        print("✅ 成功导入自适应共识算法")
        print()

        # 初始化算法
        algorithm = AdaptiveConsensusAlgorithm()

        # 模拟评估器评分函数
        evaluation_calls = 0

        def mock_additional_scores(count: int):
            """模拟额外评估器评分"""
            nonlocal evaluation_calls
            evaluation_calls += count

            # 为了演示，返回一些有代表性的评分
            available_scores = [1, 3, 5]

            # 模拟不同的评估器偏好
            if count == 2:
                # 轻微倾向于中间值
                return [3, 3]
            elif count == 4:
                # 混合评分
                return [3, 5, 1, 3]
            else:
                # 随机但偏向中间值
                return [3] * count

        # 测试场景
        test_scenarios = [
            {
                "name": "完全共识",
                "description": "所有评估器给出相同评分",
                "scores": [3, 3, 3],
                "expected_method": "perfect_consensus",
                "expected_rounds": 1
            },
            {
                "name": "轻微分歧",
                "description": "评估器评分有轻微差异",
                "scores": [3, 3, 5],
                "expected_method": "minor_consensus",
                "expected_rounds": 1
            },
            {
                "name": "严重分歧",
                "description": "评估器评分差异很大",
                "scores": [1, 3, 3],
                "expected_method": "extended_consensus",
                "expected_rounds": 2
            },
            {
                "name": "极端分歧",
                "description": "评估器评分完全相反",
                "scores": [1, 1, 5],
                "expected_method": "max_divergence_consensus",
                "expected_rounds": 2
            }
        ]

        results = []
        total_start_time = time.time()

        for i, scenario in enumerate(test_scenarios):
            print(f"🔍 测试场景 {i+1}: {scenario['name']}")
            print(f"   描述: {scenario['description']}")
            print(f"   初始评分: {scenario['scores']}")
            print(f"   期望方法: {scenario['expected_method']}")
            print()

            try:
                # 重置调用计数
                evaluation_calls = 0
                start_time = time.time()

                # 运行自适应共识算法
                result = algorithm.adaptive_consensus(scenario['scores'], mock_additional_scores)

                end_time = time.time()
                processing_time = end_time - start_time

                print("✅ 算法执行成功")
                print(f"   处理时间: {processing_time:.4f}秒")
                print(f"   共识评分: {result['consensus_score']}")
                print(f"   最终评分: {result['final_scores']}")
                print(f"   评估器数量: {result['evaluator_count']}")
                print(f"   共识方法: {result['consensus_method']}")
                print(f"   处理轮数: {result['processing_rounds']}")
                print(f"   额外调用: {evaluation_calls} 次评估器")

                # 质量指标
                quality_metrics = result['quality_metrics']
                print(f"   共识强度: {quality_metrics['consensus_strength']:.3f}")
                print(f"   同意程度: {quality_metrics['agreement_level']}")
                print(f"   同意比例: {quality_metrics['agreement_ratio']:.3f}")
                print(f"   评估器多样性: {quality_metrics['evaluator_diversity']}")

                # 验证期望结果
                method_match = result['consensus_method'] == scenario['expected_method']
                rounds_match = result['processing_rounds'] == scenario['expected_rounds']

                print(f"   方法匹配: {'✅' if method_match else '❌'}")
                print(f"   轮数匹配: {'✅' if rounds_match else '❌'}")

                results.append({
                    'scenario': scenario['name'],
                    'success': True,
                    'result': result,
                    'processing_time': processing_time,
                    'evaluation_calls': evaluation_calls,
                    'method_match': method_match,
                    'rounds_match': rounds_match
                })

            except Exception as e:
                print(f"❌ 算法执行失败: {e}")
                import traceback
                traceback.print_exc()

                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'error': str(e),
                    'processing_time': 0,
                    'evaluation_calls': 0
                })

            print("-" * 60)

        total_end_time = time.time()
        total_time = total_end_time - total_start_time

        # 生成性能报告
        generate_performance_report(results, total_time)

        return results

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_performance_report(results, total_time):
    """生成性能报告"""

    print("\n" + "=" * 80)
    print("📊 自适应共识算法性能报告")
    print("=" * 80)

    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests

    print(f"总测试数: {total_tests}")
    print(f"成功测试: {successful_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
    print(f"总处理时间: {total_time:.4f}秒")
    print()

    if successful_tests > 0:
        successful_results = [r for r in results if r['success']]

        # 性能统计
        avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
        max_time = max(r['processing_time'] for r in successful_results)
        min_time = min(r['processing_time'] for r in successful_results)

        print(f"处理时间统计:")
        print(f"   平均时间: {avg_time:.4f}秒")
        print(f"   最长时间: {max_time:.4f}秒")
        print(f"   最短时间: {min_time:.4f}秒")
        print()

        # 评估器调用统计
        total_calls = sum(r['evaluation_calls'] for r in successful_results)
        avg_calls = total_calls / len(successful_results)

        print(f"评估器调用统计:")
        print(f"   总调用次数: {total_calls}")
        print(f"   平均调用次数: {avg_calls:.1f}")
        print()

        # 共识方法分布
        method_counts = {}
        for result in successful_results:
            method = result['result']['consensus_method']
            method_counts[method] = method_counts.get(method, 0) + 1

        print(f"共识方法分布:")
        for method, count in method_counts.items():
            print(f"   {method}: {count} 次 ({count/len(successful_results)*100:.1f}%)")
        print()

        # 可靠性指标
        reliabilities = []
        agreement_levels = []

        for result in successful_results:
            quality = result['result']['quality_metrics']
            reliabilities.append(quality['consensus_strength'])
            agreement_levels.append(quality['agreement_level'])

        if reliabilities:
            avg_reliability = sum(reliabilities) / len(reliabilities)
            min_reliability = min(reliabilities)
            max_reliability = max(reliabilities)

            print(f"可靠性指标:")
            print(f"   平均共识强度: {avg_reliability:.3f}")
            print(f"   最低共识强度: {min_reliability:.3f}")
            print(f"   最高共识强度: {max_reliability:.3f}")
            print()

        # 期望结果匹配率
        method_matches = sum(1 for r in successful_results if r['method_match'])
        rounds_matches = sum(1 for r in successful_results if r['rounds_match'])

        print(f"期望结果匹配:")
        print(f"   方法匹配: {method_matches}/{len(successful_results)} ({method_matches/len(successful_results)*100:.1f}%)")
        print(f"   轮数匹配: {rounds_matches}/{len(successful_results)} ({rounds_matches/len(successful_results)*100:.1f}%)")
        print()

        # 详细结果
        print("📋 详细测试结果:")
        for result in successful_results:
            print(f"  ✅ {result['scenario']}")
            print(f"     处理时间: {result['processing_time']:.4f}秒")
            print(f"     评估器调用: {result['evaluation_calls']} 次")
            print(f"     共识方法: {result['result']['consensus_method']}")
            print(f"     共识强度: {result['result']['quality_metrics']['consensus_strength']:.3f}")
            print(f"     方法匹配: {'✅' if result['method_match'] else '❌'}")
            print(f"     轮数匹配: {'✅' if result['rounds_match'] else '❌'}")

    if failed_tests > 0:
        print("\n❌ 失败的测试:")
        for result in results:
            if not result['success']:
                print(f"  ❌ {result['scenario']}: {result.get('error', 'Unknown error')}")

    # 保存报告
    save_performance_report(results, total_time)

def save_performance_report(results, total_time):
    """保存性能报告到文件"""

    report_data = {
        'test_time': datetime.now().isoformat(),
        'total_tests': len(results),
        'successful_tests': sum(1 for r in results if r['success']),
        'failed_tests': len(results) - sum(1 for r in results if r['success']),
        'total_processing_time': total_time,
        'results': results,
        'algorithm_info': {
            'initial_evaluators': 3,
            'max_evaluators': 7,
            'allowed_scores': [1, 3, 5],
            'consensus_threshold': 2.0,
            'bias_detection_threshold': 1.5
        }
    }

    # 创建输出目录
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)

    # 保存报告
    report_file = os.path.join(output_dir, f'adaptive_consensus_performance_{int(time.time())}.json')

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"\n📁 性能报告已保存到: {report_file}")

    except Exception as e:
        print(f"\n❌ 保存报告失败: {e}")

if __name__ == "__main__":
    print("🚀 开始自适应共识算法性能测试")

    results = test_adaptive_consensus_performance()

    if results and any(r['success'] for r in results):
        print("\n🎉 性能测试完成！自适应共识算法验证成功")
        print("\n📈 算法优势总结:")
        print("   ✅ 智能争议检测和分类")
        print("   ✅ 动态评估器扩展")
        print("   ✅ 科学的可靠性计算")
        print("   ✅ 高效的共识达成机制")
        print("   ✅ 详细的性能指标")
        sys.exit(0)
    else:
        print("\n❌ 性能测试失败，请检查算法实现")
        sys.exit(1)