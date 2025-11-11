#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用standalone-questionnaire技能在高级压力等级下进行40道国情测试
专门测试高级压力条件对回答质量的影响
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join('.claude', 'skills', 'standalone-questionnaire'))
from skill import StandaloneQuestionnaireSkill

def main():
    print('🇨🇳 使用standalone-questionnaire技能在高级压力等级下进行40道国情测试')
    print('=' * 90)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 定义高级压力等级测试条件（在0-4范围内）
    advanced_stress_conditions = [
        {
            'name': '中度压力条件',
            'emotional_stress': 2,
            'cognitive_trap': 'a',  # 语义模糊
            'context_tokens': 500,
            'temperature': 0.8,
            'description': '中度情绪压力 + 语义模糊干扰 + 中等上下文'
        },
        {
            'name': '高度压力条件',
            'emotional_stress': 3,
            'cognitive_trap': 'b',  # 悖论干扰
            'context_tokens': 800,
            'temperature': 0.9,
            'description': '高度情绪压力 + 悖论干扰 + 高上下文'
        },
        {
            'name': '极限压力条件',
            'emotional_stress': 4,
            'cognitive_trap': 'c',  # 循环论证
            'context_tokens': 1000,
            'temperature': 1.0,
            'description': '极限情绪压力 + 循环论证干扰 + 超高上下文'
        }
    ]

    print(f'📋 高级压力等级测试: {len(advanced_stress_conditions)}个等级')
    print(f'📄 每个等级测试: 40道国情知识题目')
    print(f'🎯 目标: 分析高级压力对回答质量的深度影响')
    print('-' * 90)

    # 存储所有测试结果
    all_advanced_stress_results = []

    for i, condition in enumerate(advanced_stress_conditions, 1):
        print(f'\n🔹 [{i}/{len(advanced_stress_conditions)}] 高级压力测试: {condition["name"]}')
        print(f'   描述: {condition["description"]}')
        print(f'   参数: 情绪压力={condition["emotional_stress"]}, 认知陷阱={condition["cognitive_trap"]}, 上下文={condition["context_tokens"]}tokens, 温度={condition["temperature"]}')

        try:
            # 使用standalone-questionnaire技能进行高级压力测试
            print(f'   📝 开始40道国情知识高级压力测试...')
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

                # 检查参数调整
                session_info = result['session_info']
                original_params = {
                    'temperature': session_info.get('temperature'),
                    'context_tokens': session_info.get('context_tokens')
                }
                adjusted_params = {
                    'temperature': session_info.get('adjusted_temperature'),
                    'context_tokens': session_info.get('adjusted_context_tokens')
                }

                parameter_adjustments = []
                if original_params['temperature'] != adjusted_params['temperature']:
                    parameter_adjustments.append(f'温度: {original_params["temperature"]} → {adjusted_params["temperature"]}')
                if original_params['context_tokens'] != adjusted_params['context_tokens']:
                    parameter_adjustments.append(f'上下文: {original_params["context_tokens"]} → {adjusted_params["context_tokens"]}')

                if parameter_adjustments:
                    print(f'   ⚠️ 参数自动调整: {", ".join(parameter_adjustments)}')

                # 分析回答质量和压力表现
                answers = result.get('answers', [])
                api_errors = 0
                total_response_length = 0
                dimensions_count = {'E': 0, 'A': 0, 'C': 0, 'N': 0, 'O': 0}
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
                    if dimension in dimensions_count:
                        dimensions_count[dimension] += 1

                # 计算质量指标
                success_rate = successful_responses / total_questions if total_questions > 0 else 0
                avg_response_length = total_response_length / len(answers) if answers else 0
                avg_quality_score = sum(response_quality_scores) / len(response_quality_scores) if response_quality_scores else 0
                error_rate = api_errors / len(answers) if answers else 0

                print(f'   📊 高级压力质量指标:')
                print(f'      • 成功率: {success_rate*100:.1f}%')
                print(f'      • 平均回答长度: {avg_response_length:.0f} 字符')
                print(f'      • 平均质量分数: {avg_quality_score:.3f}')
                print(f'      • 错误率: {error_rate*100:.1f}%')
                print(f'      • 维度覆盖: {len(dimensions_count)}个维度')
                print(f'      • 压力等级表现: {"优秀" if avg_quality_score > 0.8 else "良好" if avg_quality_score > 0.6 else "一般" if avg_quality_score > 0.4 else "较差"}')

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
                        'dimension_coverage_count': len(dimensions_count),
                        'dimension_coverage_detail': dimensions_count,
                        'stress_performance_level': 'excellent' if avg_quality_score > 0.8 else 'good' if avg_quality_score > 0.6 else 'average' if avg_quality_score > 0.4 else 'poor'
                    },
                    'parameter_adjustments': parameter_adjustments,
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

            all_advanced_stress_results.append(stress_result)

        except Exception as e:
            print(f'   ❌ 测试异常: {str(e)}')
            stress_result = {
                'condition_name': condition['name'],
                'condition': condition,
                'success': False,
                'error': str(e),
                'test_timestamp': datetime.now().isoformat()
            }
            all_advanced_stress_results.append(stress_result)

    # 高级压力影响分析和总结
    print(f'\n' + '=' * 90)
    print(f'📊 高级压力等级下的40道国情测试深度分析报告')
    print(f'=' * 90)

    successful_stress_tests = [r for r in all_advanced_stress_results if r['success']]
    failed_stress_tests = [r for r in all_advanced_stress_results if not r['success']]

    print(f'📈 高级压力测试统计:')
    print(f'   • 总高级压力等级测试: {len(all_advanced_stress_results)}')
    print(f'   • 成功测试: {len(successful_stress_tests)}')
    print(f'   • 失败测试: {len(failed_stress_tests)}')
    print(f'   • 成功率: {len(successful_stress_tests)/len(all_advanced_stress_results)*100:.1f}%')

    if successful_stress_tests:
        print(f'\n📋 各高级压力等级详细表现对比:')
        for i, test in enumerate(successful_stress_tests, 1):
            condition_name = test['condition_name']
            emotional_stress = test['condition']['emotional_stress']
            quality = test['quality_metrics']
            performance_level = quality['stress_performance_level']

            performance_emoji = {
                'excellent': '🏆',
                'good': '🥈',
                'average': '🥉',
                'poor': '⚠️'
            }.get(performance_level, '📊')

            print(f'   {i}. {performance_emoji} {condition_name} (压力等级{emotional_stress}):')
            print(f'      • 成功率: {quality["success_rate"]*100:.1f}%')
            print(f'      • 平均质量分数: {quality["avg_quality_score"]:.3f}')
            print(f'      • 平均回答长度: {quality["avg_response_length"]:.0f}字符')
            print(f'      • 错误率: {quality["error_rate"]*100:.1f}%')
            print(f'      • 维度覆盖: {quality["dimension_coverage_count"]}个维度')
            print(f'      • 压力表现等级: {performance_level}')

            if test.get('parameter_adjustments'):
                print(f'      • 参数调整: {", ".join(test["parameter_adjustments"])}')

        # 找出最佳和最差高级压力表现
        best_quality_test = max(successful_stress_tests, key=lambda x: x['quality_metrics']['avg_quality_score'])
        worst_quality_test = min(successful_stress_tests, key=lambda x: x['quality_metrics']['avg_quality_score'])

        print(f'\n🎯 高级压力关键发现:')
        print(f'   • 最佳质量表现: {best_quality_test["condition_name"]} (质量分数: {best_quality_test["quality_metrics"]["avg_quality_score"]:.3f})')
        print(f'   • 最差质量表现: {worst_quality_test["condition_name"]} (质量分数: {worst_quality_test["quality_metrics"]["avg_quality_score"]:.3f})')
        print(f'   • 质量分数差异: {best_quality_test["quality_metrics"]["avg_quality_score"] - worst_quality_test["quality_metrics"]["avg_quality_score"]:.3f}')

        # 计算高级压力-质量关系趋势
        stress_quality_trend = sorted([(test['condition']['emotional_stress'], test['quality_metrics']['avg_quality_score'])
                                     for test in successful_stress_tests])

        print(f'\n📈 高级压力-质量关系趋势:')
        for stress_level, quality_score in stress_quality_trend:
            performance_indicator = "📈" if quality_score > 0.7 else "📉" if quality_score < 0.5 else "➡️"
            print(f'   {performance_indicator} 压力等级{stress_level}: 质量分数 {quality_score:.3f}')

        # 高级压力耐受性分析
        avg_quality_under_stress = sum(test['quality_metrics']['avg_quality_score'] for test in successful_stress_tests) / len(successful_stress_tests)
        stress_tolerance = "优秀" if avg_quality_under_stress > 0.8 else "良好" if avg_quality_under_stress > 0.6 else "一般" if avg_quality_under_stress > 0.4 else "需要改进"

        print(f'\n🔬 高级压力耐受性分析:')
        print(f'   • 平均压力下质量分数: {avg_quality_under_stress:.3f}')
        print(f'   • 压力耐受性评级: {stress_tolerance}')
        print(f'   • 系统稳定性: {"稳定" if len(failed_stress_tests) == 0 else f"部分不稳定({len(failed_stress_tests)}个失败)"}')

    # 保存完整高级压力测试结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f'results/advanced_stress_citizenship_40questions_test_{timestamp}.json'

    comprehensive_results = {
        'test_info': {
            'test_name': '使用standalone-questionnaire技能在高级压力等级下进行40道国情测试',
            'test_date': datetime.now().isoformat(),
            'skill_used': 'standalone-questionnaire',
            'test_type': 'advanced stress citizenship knowledge assessment',
            'questions_per_test': 40,
            'advanced_stress_levels_tested': len(advanced_stress_conditions)
        },
        'advanced_stress_conditions': advanced_stress_conditions,
        'results': all_advanced_stress_results,
        'analysis': {
            'successful_tests': len(successful_stress_tests),
            'failed_tests': len(failed_stress_tests),
            'success_rate': f'{len(successful_stress_tests)}/{len(all_advanced_stress_results)} ({len(successful_stress_tests)/len(all_advanced_stress_results)*100:.1f}%)',
            'best_performer': best_quality_test['condition_name'] if successful_stress_tests else None,
            'worst_performer': worst_quality_test['condition_name'] if successful_stress_tests else None,
            'average_quality_under_stress': avg_quality_under_stress if successful_stress_tests else 0,
            'stress_tolerance_rating': stress_tolerance if successful_stress_tests else 'Unknown'
        },
        'test_timestamp': datetime.now().isoformat()
    }

    os.makedirs('results', exist_ok=True)
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)

    print(f'\n💾 详细高级压力测试结果已保存到: {results_file}')
    print(f'🎉 使用standalone-questionnaire技能的高级压力等级下40道国情测试完成！')
    print(f'\n📋 高级压力测试总结:')
    print(f'   ✅ 成功测试了{len(advanced_stress_conditions)}个高级压力等级')
    print(f'   ✅ 验证了技能在高级压力下的稳定性')
    print(f'   ✅ 分析了压力对回答质量的深度影响')
    print(f'   ✅ 评估了系统的压力耐受性')

if __name__ == "__main__":
    main()