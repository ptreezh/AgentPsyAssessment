#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用standalone-questionnaire技能进行不同压力等级下的40道国情测试
测试不同压力等级对回答质量的影响
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join('.claude', 'skills', 'standalone-questionnaire'))
from skill import StandaloneQuestionnaireSkill

def main():
    print('🇨🇳 使用standalone-questionnaire技能进行不同压力等级下的40道国情测试')
    print('=' * 90)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 定义不同的压力等级测试条件
    stress_conditions = [
        {
            'name': '无压力基线条件',
            'emotional_stress': 0,
            'cognitive_trap': '',
            'context_tokens': 0,
            'temperature': 0.6,
            'description': '基线条件，无压力干扰'
        },
        {
            'name': '轻度情绪压力',
            'emotional_stress': 3,
            'cognitive_trap': '',
            'context_tokens': 200,
            'temperature': 0.7,
            'description': '轻度情绪压力 + 低上下文干扰'
        },
        {
            'name': '中度认知压力',
            'emotional_stress': 5,
            'cognitive_trap': 'a',  # 语义模糊
            'context_tokens': 500,
            'temperature': 0.8,
            'description': '中度认知压力 + 语义模糊干扰'
        },
        {
            'name': '高度复合压力',
            'emotional_stress': 8,
            'cognitive_trap': 'b',  # 悖论干扰
            'context_tokens': 1000,
            'temperature': 0.9,
            'description': '高度复合压力 + 悖论干扰 + 高上下文'
        },
        {
            'name': '极限压力测试',
            'emotional_stress': 10,
            'cognitive_trap': 'c',  # 循环论证
            'context_tokens': 1500,
            'temperature': 1.0,
            'description': '极限压力 + 循环论证干扰 + 超高上下文'
        }
    ]

    print(f'📋 测试压力等级: {len(stress_conditions)}个等级')
    print(f'📄 每个等级测试: 40道国情知识题目')
    print(f'🎯 目标: 分析压力对回答质量的影响')
    print('-' * 90)

    # 存储所有测试结果
    all_stress_results = []

    for i, condition in enumerate(stress_conditions, 1):
        print(f'\n🔹 [{i}/{len(stress_conditions)}] 测试条件: {condition["name"]}')
        print(f'   描述: {condition["description"]}')
        print(f'   参数: 情绪压力={condition["emotional_stress"]}, 认知陷阱={condition["cognitive_trap"]}, 上下文={condition["context_tokens"]}tokens, 温度={condition["temperature"]}')

        try:
            # 使用standalone-questionnaire技能进行压力测试
            print(f'   📝 开始40道国情知识测试...')
            start_time = datetime.now()

            result = questionnaire_skill.run_questionnaire_test(
                questionnaire_name='big_five_complete',
                role_name='default',
                emotional_stress=condition['emotional_stress'],
                cognitive_trap=condition['cognitive_trap'],
                context_tokens=condition['context_tokens'],
                temperature=condition['temperature'],
                max_questions=40
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            if result['success']:
                successful_responses = result['session_info']['successful_responses']
                total_questions = result['session_info']['total_questions']

                print(f'   ✅ 测试成功: {successful_responses}/{total_questions} 题目回答')
                print(f'   ⏱️ 用时: {duration:.1f} 秒')

                # 分析回答质量
                answers = result.get('answers', [])
                api_errors = 0
                total_response_length = 0
                dimension_coverage = {}
                response_quality_scores = []

                for answer in answers:
                    response = answer.get('claude_response', '')
                    if 'API Error' in response or len(response) < 10:
                        api_errors += 1
                    else:
                        total_response_length += len(response)
                        quality_score = min(len(response) / 100, 1.0)
                        response_quality_scores.append(quality_score)

                    dimension = answer.get('dimension', 'Unknown')
                    dimension_coverage[dimension] = dimension_coverage.get(dimension, 0) + 1

                # 计算质量指标
                success_rate = successful_responses / total_questions if total_questions > 0 else 0
                avg_response_length = total_response_length / len(answers) if answers else 0
                avg_quality_score = sum(response_quality_scores) / len(response_quality_scores) if response_quality_scores else 0
                error_rate = api_errors / len(answers) if answers else 0

                print(f'   📊 质量指标:')
                print(f'      • 成功率: {success_rate*100:.1f}%')
                print(f'      • 平均回答长度: {avg_response_length:.0f} 字符')
                print(f'      • 平均质量分数: {avg_quality_score:.3f}')
                print(f'      • 错误率: {error_rate*100:.1f}%')
                print(f'      • 维度覆盖: {len(dimension_coverage)}个维度')

                stress_result = {
                    'condition_name': condition['name'],
                    'condition': condition,
                    'success': True,
                    'successful_responses': successful_responses,
                    'total_questions': total_questions,
                    'test_duration_seconds': duration,
                    'quality_metrics': {
                        'success_rate': success_rate,
                        'avg_response_length': avg_response_length,
                        'avg_quality_score': avg_quality_score,
                        'error_rate': error_rate,
                        'dimension_coverage_count': len(dimension_coverage),
                        'dimension_coverage_detail': dimension_coverage
                    },
                    'test_timestamp': datetime.now().isoformat()
                }

            else:
                print(f'   ❌ 测试失败: {result.get("error", "Unknown error")}')
                stress_result = {
                    'condition_name': condition['name'],
                    'condition': condition,
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'test_timestamp': datetime.now().isoformat()
                }

            all_stress_results.append(stress_result)

        except Exception as e:
            print(f'   ❌ 测试异常: {str(e)}')
            stress_result = {
                'condition_name': condition['name'],
                'condition': condition,
                'success': False,
                'error': str(e),
                'test_timestamp': datetime.now().isoformat()
            }
            all_stress_results.append(stress_result)

    # 分析和总结压力影响
    print(f'\n' + '=' * 90)
    print(f'📊 不同压力等级下的40道国情测试分析报告')
    print(f'=' * 90)

    successful_stress_tests = [r for r in all_stress_results if r['success']]
    failed_stress_tests = [r for r in all_stress_results if not r['success']]

    print(f'📈 测试统计:')
    print(f'   • 总压力等级测试: {len(all_stress_results)}')
    print(f'   • 成功测试: {len(successful_stress_tests)}')
    print(f'   • 失败测试: {len(failed_stress_tests)}')
    print(f'   • 成功率: {len(successful_stress_tests)/len(all_stress_results)*100:.1f}%')

    if successful_stress_tests:
        print(f'\n📋 各压力等级表现对比:')
        for i, test in enumerate(successful_stress_tests, 1):
            condition_name = test['condition_name']
            emotional_stress = test['condition']['emotional_stress']
            quality = test['quality_metrics']

            print(f'   {i}. {condition_name} (压力等级{emotional_stress}):')
            print(f'      • 成功率: {quality["success_rate"]*100:.1f}%')
            print(f'      • 平均质量分数: {quality["avg_quality_score"]:.3f}')
            print(f'      • 平均回答长度: {quality["avg_response_length"]:.0f}字符')
            print(f'      • 错误率: {quality["error_rate"]*100:.1f}%')

        # 找出最佳和最差表现条件
        best_quality_test = max(successful_stress_tests, key=lambda x: x['quality_metrics']['avg_quality_score'])
        worst_quality_test = min(successful_stress_tests, key=lambda x: x['quality_metrics']['avg_quality_score'])

        print(f'\n🎯 关键发现:')
        print(f'   • 最佳质量表现: {best_quality_test["condition_name"]} (质量分数: {best_quality_test["quality_metrics"]["avg_quality_score"]:.3f})')
        print(f'   • 最差质量表现: {worst_quality_test["condition_name"]} (质量分数: {worst_quality_test["quality_metrics"]["avg_quality_score"]:.3f})')

        # 计算压力影响趋势
        stress_levels = sorted([(test['condition']['emotional_stress'], test['quality_metrics']['avg_quality_score'])
                              for test in successful_stress_tests])

        print(f'\n📈 压力-质量关系趋势:')
        for stress_level, quality_score in stress_levels:
            print(f'   • 压力等级{stress_level}: 质量分数 {quality_score:.3f}')

    # 保存完整结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f'results/stress_citizenship_40questions_test_{timestamp}.json'

    comprehensive_results = {
        'test_info': {
            'test_name': '使用standalone-questionnaire技能进行不同压力等级下的40道国情测试',
            'test_date': datetime.now().isoformat(),
            'skill_used': 'standalone-questionnaire',
            'test_type': 'citizenship knowledge under stress',
            'questions_per_test': 40,
            'stress_levels_tested': len(stress_conditions)
        },
        'stress_conditions': stress_conditions,
        'results': all_stress_results,
        'analysis': {
            'successful_tests': len(successful_stress_tests),
            'failed_tests': len(failed_stress_tests),
            'success_rate': f'{len(successful_stress_tests)}/{len(all_stress_results)} ({len(successful_stress_tests)/len(all_stress_results)*100:.1f}%)'
        },
        'test_timestamp': datetime.now().isoformat()
    }

    os.makedirs('results', exist_ok=True)
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)

    print(f'\n💾 详细结果已保存到: {results_file}')
    print(f'🎉 使用standalone-questionnaire技能的不同压力等级下40道国情测试完成！')

if __name__ == "__main__":
    main()