#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的透明流水线
验证自适应共识算法集成
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'production_pipelines', 'local_batch_production', 'single_report_pipeline'))

from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

def test_adaptive_consensus_integration():
    """测试自适应共识算法集成"""

    print("🧠 测试修改后的透明流水线")
    print("=" * 60)

    # 测试文件
    test_file = 'results/readonly-original/asses_deepseek_r1_70b_agent_big_five_50_complete2_a1_e0_t0_0_09271.json'

    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False

    try:
        # 初始化解析器和流水线
        parser = InputParser()
        pipeline = TransparentPipeline(use_cloud=True)

        print(f"📂 解析测试文件: {test_file}")
        questions = parser.parse_assessment_json(test_file)

        print(f"✅ 找到 {len(questions)} 道题目")
        print()

        # 测试前3题
        for i, question in enumerate(questions[:3]):
            print(f"🔍 测试题目 {i+1}: {question.get('question_id', 'Unknown')}")
            print(f"   题目概念: {question['question_data'].get('mapped_ipip_concept', 'Unknown')}")
            print(f"   维度: {question['question_data'].get('dimension', 'Unknown')}")

            try:
                result = pipeline.process_single_question(question, i)

                print(f"✅ 处理成功:")
                print(f"   最终评分: {result.get('final_adjusted_scores', {})}")
                print(f"   可靠性: {result.get('confidence_metrics', {}).get('overall_reliability', 0):.3f}")

                # 检查是否有新的共识方法字段
                if 'consensus_method' in result.get('confidence_metrics', {}):
                    print(f"   共识方法: {result['confidence_metrics']['consensus_method']}")

                print(f"   使用模型: {len(result.get('models_used', []))} 个")
                print(f"   处理轮数: {result.get('resolution_rounds', 0)}")

            except Exception as e:
                print(f"❌ 处理失败: {e}")
                import traceback
                traceback.print_exc()
                return False

            print("-" * 40)

        print("🎉 测试完成！自适应共识算法集成成功")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_adaptive_consensus_algorithm_directly():
    """直接测试自适应共识算法"""

    print("\n🔬 直接测试自适应共识算法")
    print("=" * 60)

    try:
        from adaptive_consensus_algorithm import AdaptiveConsensusAlgorithm

        algorithm = AdaptiveConsensusAlgorithm()

        # 模拟获取额外评估器评分的函数
        def mock_additional_scores(count: int) -> list:
            """模拟额外评估器评分"""
            # 为了演示，返回倾向于3分的评分
            return [3, 3, 5][:count]

        # 测试不同场景
        test_scenarios = [
            {
                'name': '完全共识',
                'scores': [3, 3, 3]
            },
            {
                'name': '轻微分歧',
                'scores': [3, 3, 5]
            },
            {
                'name': '严重分歧',
                'scores': [1, 3, 3]
            },
            {
                'name': '极端分歧',
                'scores': [1, 1, 5]
            }
        ]

        for scenario in test_scenarios:
            print(f"\n📊 测试场景: {scenario['name']}")
            print(f"初始评分: {scenario['scores']}")
            print("-" * 30)

            try:
                result = algorithm.adaptive_consensus(scenario['scores'], mock_additional_scores)

                print(f"✅ 共识结果:")
                print(f"   共识评分: {result['consensus_score']}")
                print(f"   最终评分: {result['final_scores']}")
                print(f"   评估器数量: {result['evaluator_count']}")
                print(f"   共识方法: {result['consensus_method']}")
                print(f"   处理轮数: {result['processing_rounds']}")
                print(f"   质量指标: {result['quality_metrics']}")

            except Exception as e:
                print(f"❌ 场景测试失败: {e}")
                return False

        print("\n🎉 自适应共识算法测试通过")
        return True

    except Exception as e:
        print(f"❌ 算法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始测试修改后的透明流水线")

    # 测试1: 直接测试自适应共识算法
    success1 = test_adaptive_consensus_algorithm_directly()

    # 测试2: 测试集成后的流水线
    success2 = test_adaptive_consensus_integration()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 所有测试通过！自适应共识算法集成成功")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查代码")
        sys.exit(1)