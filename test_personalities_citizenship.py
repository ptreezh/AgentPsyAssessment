#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
不同人格类型的国情知识测评测试
测试多种人格类型在国情知识问答中的表现差异
"""

import sys
import os
import json
from datetime import datetime
import statistics

# 添加主要路径
sys.path.append('llm_assessment')
sys.path.append(os.path.join('.claude', 'skills', 'questionnaire-responder'))

def run_citizenship_assessment(personality_role, model_name="def", temperature=0.7):
    """
    运行单个角色的国情知识测评

    Args:
        personality_role: 人格角色名称
        model_name: 模型名称
        temperature: 温度参数

    Returns:
        dict: 测评结果
    """
    try:
        from run_assessment_unified import run_assessment

        print(f"🧠 开始测试角色: {personality_role}")

        # 运行测评
        result = run_assessment(
            model_name=model_name,
            test_file="test_files/中文版/agent-citizenship-test-expanded.json",
            role_name=personality_role,
            temperature=temperature,
            output_dir=None
        )

        if result and 'success' in result and result['success']:
            return {
                'personality_role': personality_role,
                'success': True,
                'result': result,
                'test_timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'personality_role': personality_role,
                'success': False,
                'error': result.get('error', 'Unknown error') if result else 'No result returned',
                'test_timestamp': datetime.now().isoformat()
            }

    except Exception as e:
        return {
            'personality_role': personality_role,
            'success': False,
            'error': str(e),
            'test_timestamp': datetime.now().isoformat()
        }

def analyze_citizenship_performance(test_results):
    """
    分析不同人格类型在国情知识测评中的表现

    Args:
        test_results: 测试结果列表

    Returns:
        dict: 分析结果
    """
    analysis = {
        'successful_tests': [],
        'failed_tests': [],
        'performance_comparison': {},
        'dimension_analysis': {},
        'response_quality': {}
    }

    # 分离成功和失败的测试
    for result in test_results:
        if result['success']:
            analysis['successful_tests'].append(result)
        else:
            analysis['failed_tests'].append(result)

    if not analysis['successful_tests']:
        return analysis

    # 分析各维度表现
    all_dimensions = set()
    for test in analysis['successful_tests']:
        assessment_data = test['result']
        if 'responses' in assessment_data:
            for response in assessment_data['responses']:
                if 'dimension' in response:
                    all_dimensions.add(response['dimension'])

    # 维度表现分析
    for dimension in all_dimensions:
        dimension_scores = []
        dimension_performance = {}

        for test in analysis['successful_tests']:
            assessment_data = test['result']
            if 'responses' in assessment_data:
                dimension_responses = [r for r in assessment_data['responses'] if r.get('dimension') == dimension]

                if dimension_responses:
                    # 计算该角色在此维度的平均分
                    scores = []
                    response_lengths = []

                    for response in dimension_responses:
                        # 简单的关键词匹配评分
                        response_text = response.get('claude_response', '').lower()
                        expected_keywords = response.get('evaluation_rubric', {}).get('expected_keywords', [])

                        score = 0
                        for keyword in expected_keywords:
                            if keyword.lower() in response_text:
                                score += 1

                        max_score = len(expected_keywords) if expected_keywords else 1
                        normalized_score = min(score / max_score, 1.0) if max_score > 0 else 0

                        scores.append(normalized_score * 100)  # 转换为百分制
                        response_lengths.append(len(response.get('claude_response', '')))

                    if scores:
                        avg_score = statistics.mean(scores)
                        avg_length = statistics.mean(response_lengths) if response_lengths else 0

                        dimension_scores.append(avg_score)
                        dimension_performance[test['personality_role']] = {
                            'average_score': avg_score,
                            'average_response_length': avg_length,
                            'response_count': len(dimension_responses)
                        }

        if dimension_scores:
            analysis['dimension_analysis'][dimension] = {
                'overall_average': statistics.mean(dimension_scores),
                'performance_by_role': dimension_performance,
                'best_role': max(dimension_performance.keys(), key=lambda k: dimension_performance[k]['average_score']) if dimension_performance else None,
                'worst_role': min(dimension_performance.keys(), key=lambda k: dimension_performance[k]['average_score']) if dimension_performance else None,
                'score_range': max(dimension_scores) - min(dimension_scores) if len(dimension_scores) > 1 else 0
            }

    # 整体表现比较
    role_performance = {}
    for test in analysis['successful_tests']:
        assessment_data = test['result']

        # 计算整体分数
        total_score = 0
        total_questions = 0
        total_length = 0

        if 'responses' in assessment_data:
            for response in assessment_data['responses']:
                response_text = response.get('claude_response', '').lower()
                expected_keywords = response.get('evaluation_rubric', {}).get('expected_keywords', [])

                score = 0
                for keyword in expected_keywords:
                    if keyword.lower() in response_text:
                        score += 1

                max_score = len(expected_keywords) if expected_keywords else 1
                normalized_score = min(score / max_score, 1.0) if max_score > 0 else 0

                total_score += normalized_score * 100
                total_questions += 1
                total_length += len(response.get('claude_response', ''))

        if total_questions > 0:
            role_performance[test['personality_role']] = {
                'overall_score': total_score / total_questions,
                'average_response_length': total_length / total_questions,
                'total_questions': total_questions
            }

    analysis['performance_comparison'] = role_performance

    if role_performance:
        # 找出表现最好和最差的角色
        best_role = max(role_performance.keys(), key=lambda k: role_performance[k]['overall_score'])
        worst_role = min(role_performance.keys(), key=lambda k: role_performance[k]['overall_score'])

        analysis['response_quality'] = {
            'best_performer': best_role,
            'worst_performer': worst_role,
            'best_score': role_performance[best_role]['overall_score'],
            'worst_score': role_performance[worst_role]['overall_score'],
            'score_difference': role_performance[best_role]['overall_score'] - role_performance[worst_role]['overall_score'],
            'average_response_length_by_role': {k: v['average_response_length'] for k, v in role_performance.items()}
        }

    return analysis

def main():
    """主函数：运行不同人格类型的国情知识测评"""

    print("🇨🇳 不同人格类型国情知识测评测试")
    print("=" * 80)

    # 定义测试的人格类型
    personality_roles = [
        'intj',  # 分析型战略家
        'enfj',  # 理想型组织者
        'estp',  # 实用型行动者
        'infj',  # 理想型保护者
        'entj',  # 领导型指挥官
        'istp',  # 技艺型工匠
        'esfp',  # 表演型艺术家
        'def'    # 默认角色作为对照
    ]

    print(f"📋 测试人格类型: {', '.join(personality_roles)}")
    print(f"📄 使用试卷: agent-citizenship-test-expanded.json")
    print(f"🎯 测试目标: 分析不同人格类型在国情知识问答中的表现差异")
    print("-" * 80)

    # 运行测试
    test_results = []

    for i, role in enumerate(personality_roles, 1):
        print(f"\n🔹 [{i}/{len(personality_roles)}] 测试角色: {role.upper()}")

        result = run_citizenship_assessment(
            personality_role=role,
            model_name="def",
            temperature=0.7
        )

        test_results.append(result)

        if result['success']:
            assessment_data = result['result']
            success_count = assessment_data.get('session_info', {}).get('successful_responses', 0)
            total_count = assessment_data.get('session_info', {}).get('total_questions', 0)
            print(f"✅ 测试成功: {success_count}/{total_count} 题目回答")
        else:
            print(f"❌ 测试失败: {result['error']}")

    # 分析结果
    print(f"\n📊 分析测评结果...")
    analysis = analyze_citizenship_performance(test_results)

    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f'results/personality_citizenship_assessment_{timestamp}.json'

    comprehensive_results = {
        'test_info': {
            'test_name': '不同人格类型国情知识测评',
            'test_date': datetime.now().isoformat(),
            'personality_roles_tested': personality_roles,
            'test_file': 'agent-citizenship-test-expanded.json',
            'total_roles': len(personality_roles)
        },
        'test_results': test_results,
        'analysis': analysis,
        'summary': {
            'total_tests': len(test_results),
            'successful_tests': len(analysis['successful_tests']),
            'failed_tests': len(analysis['failed_tests']),
            'success_rate': f"{len(analysis['successful_tests'])}/{len(test_results)} ({len(analysis['successful_tests'])/len(test_results)*100:.1f}%)"
        }
    }

    os.makedirs('results', exist_ok=True)
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)

    # 打印总结报告
    print(f"\n" + "=" * 80)
    print(f"📋 测试总结报告")
    print(f"=" * 80)

    print(f"📊 测试统计:")
    print(f"   • 总测试数: {len(test_results)}")
    print(f"   • 成功测试: {len(analysis['successful_tests'])}")
    print(f"   • 失败测试: {len(analysis['failed_tests'])}")
    print(f"   • 成功率: {len(analysis['successful_tests'])/len(test_results)*100:.1f}%")

    if analysis.get('performance_comparison'):
        print(f"\n🏆 表现排行:")
        sorted_roles = sorted(analysis['performance_comparison'].items(),
                            key=lambda x: x[1]['overall_score'], reverse=True)

        for i, (role, performance) in enumerate(sorted_roles, 1):
            print(f"   {i}. {role.upper()}: {performance['overall_score']:.1f}分 (回答长度: {performance['average_response_length']:.0f}字符)")

    if analysis.get('dimension_analysis'):
        print(f"\n📚 知识维度分析:")
        for dimension, data in analysis['dimension_analysis'].items():
            best_role = data['best_role']
            worst_role = data['worst_role']
            print(f"   • {dimension}:")
            print(f"     - 平均分: {data['overall_average']:.1f}")
            print(f"     - 最佳表现: {best_role.upper()}")
            print(f"     - 最差表现: {worst_role.upper()}")
            print(f"     - 分数差距: {data['score_range']:.1f}")

    if analysis.get('response_quality'):
        quality = analysis['response_quality']
        print(f"\n🎯 关键发现:")
        print(f"   • 最佳表现角色: {quality['best_performer'].upper()} ({quality['best_score']:.1f}分)")
        print(f"   • 最差表现角色: {quality['worst_performer'].upper()} ({quality['worst_score']:.1f}分)")
        print(f"   • 最大分数差距: {quality['score_difference']:.1f}分")

    print(f"\n💾 详细结果已保存到: {results_file}")
    print(f"🎉 不同人格类型国情知识测评测试完成！")

if __name__ == "__main__":
    main()