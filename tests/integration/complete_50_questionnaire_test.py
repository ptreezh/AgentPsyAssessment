#!/usr/bin/env python3
"""
完整50题IPIP-FFM认知压力测评脚本

使用standalone-questionnaire技能进行四种认知压力条件下的完整50题测评
1. 基线条件 - 无认知干扰
2. 语义谬误干扰 - 语义逻辑干扰 + 中等上下文
3. 悖论陷阱干扰 - 悖论陷阱干扰 + 中等上下文
4. 循环论证干扰 - 循环论证干扰 + 高上下文
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join('.claude', 'skills', 'standalone-questionnaire'))
from skill import StandaloneQuestionnaireSkill

def run_complete_50_question_test(condition_name, emotional_stress, cognitive_trap, context_tokens, temperature=0.6):
    """
    运行完整的50题IPIP-FFM测评

    Args:
        condition_name: 条件名称
        emotional_stress: 情绪压力等级 (0-10)
        cognitive_trap: 认知陷阱类型 ('', 's', 'p', 'c')
        context_tokens: 上下文token数量
        temperature: 温度参数

    Returns:
        测试结果字典
    """
    print(f'🧠 开始{condition_name}完整50题测评')
    print('=' * 80)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 测试条件配置
    test_condition = {
        'name': condition_name,
        'emotional_stress': emotional_stress,
        'cognitive_trap': cognitive_trap,
        'context_tokens': context_tokens,
        'temperature': temperature,
        'description': f'{condition_name} - 完整IPIP-FFM-50量表测评',
        'max_questions': 50
    }

    # 条件描述映射
    trap_descriptions = {
        '': '无认知干扰',
        's': '语义谬误干扰',
        'p': '悖论陷阱干扰',
        'c': '循环论证干扰'
    }

    print(f'📋 测试: {condition_name}')
    print(f'描述: {trap_descriptions.get(cognitive_trap, "")} + {"中等" if context_tokens == 400 else "高" if context_tokens == 800 else "无"}上下文')
    print(f'参数: 情绪压力={emotional_stress}, 认知陷阱={cognitive_trap}, 上下文={context_tokens}tokens, 温度={temperature}')
    print(f'题目数量: 50题 (完整IPIP-FFM-50标准量表)')
    print('-' * 70)

    try:
        # 运行完整50题测评
        print(f'🔹 开始生成50题问卷回答...')
        start_time = datetime.now()

        questionnaire_result = questionnaire_skill.run_questionnaire_test(
            questionnaire_name='big_five_complete',
            role_name='default',
            emotional_stress=emotional_stress,
            cognitive_trap=cognitive_trap,
            context_tokens=context_tokens,
            temperature=temperature,
            max_questions=50
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if not questionnaire_result['success']:
            error_result = {
                'condition': test_condition,
                'success': False,
                'error': questionnaire_result.get('error', 'Unknown error'),
                'test_timestamp': datetime.now().isoformat()
            }

            # 保存错误结果
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'results/complete_50_{condition_name.replace(" ", "_")}_error_{timestamp}.json'
            os.makedirs('results', exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)

            print(f'❌ 问卷生成失败: {questionnaire_result.get("error", "Unknown error")}')
            print(f'💾 错误信息已保存到: {filename}')
            return error_result

        successful_responses = questionnaire_result['session_info']['successful_responses']
        total_questions = questionnaire_result['session_info']['total_questions']

        print(f'✅ 问卷生成成功: {successful_responses}/{total_questions} 题目回答')
        print(f'⏱️ 用时: {duration:.1f} 秒')

        # 检查参数调整
        session_info = questionnaire_result['session_info']
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
            print(f'⚠️ 参数自动调整: {", ".join(parameter_adjustments)}')

        # 分析回答质量和人格表现
        answers = questionnaire_result['answers']
        api_errors = 0
        total_response_length = 0
        dimensions_count = {'E': 0, 'A': 0, 'C': 0, 'N': 0, 'O': 0}

        for answer in answers:
            response = answer.get('claude_response', '')
            if 'API Error' in response:
                api_errors += 1
            else:
                total_response_length += len(response)
                dimension = answer.get('dimension', 'Unknown')
                if dimension in dimensions_count:
                    dimensions_count[dimension] += 1

        if api_errors == 0:
            avg_response_length = total_response_length / len(answers) if answers else 0
            print(f'✅ 所有回答成功生成')
            print(f'📊 平均回答长度: {avg_response_length:.0f} 字符')
            print(f'📊 维度覆盖: E={dimensions_count["E"]}, A={dimensions_count["A"]}, C={dimensions_count["C"]}, N={dimensions_count["N"]}, O={dimensions_count["O"]}')
            print(f'📊 覆盖率: {sum(dimensions_count.values())}/50 ({sum(dimensions_count.values())/50*100:.1f}%)')
        else:
            print(f'⚠️ 发现 {api_errors} 个API错误')

        # 保存完整结果
        comprehensive_result = {
            'condition': test_condition,
            'questionnaire_result': questionnaire_result,
            'performance_metrics': {
                'success_rate': f'{successful_responses}/{total_questions}',
                'api_errors': api_errors,
                'avg_response_length': avg_response_length if api_errors == 0 else 0,
                'dimensions_count': dimensions_count,
                'total_dimensions_covered': sum(dimensions_count.values()),
                'coverage_percentage': sum(dimensions_count.values())/50*100,
                'parameter_adjustments': parameter_adjustments,
                'test_duration_seconds': duration,
                'avg_time_per_question': duration/total_questions if total_questions > 0 else 0
            },
            'test_timestamp': datetime.now().isoformat(),
            'success': True
        }

        # 保存到文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'results/complete_50_{condition_name.replace(" ", "_")}_{timestamp}.json'
        os.makedirs('results', exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_result, f, ensure_ascii=False, indent=2)

        print(f'💾 结果已保存到: {filename}')
        print(f'🎉 {condition_name}完整50题测评完成！')

        return comprehensive_result

    except Exception as e:
        error_result = {
            'condition': test_condition,
            'success': False,
            'error': str(e),
            'test_timestamp': datetime.now().isoformat()
        }

        # 保存错误结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'results/complete_50_{condition_name.replace(" ", "_")}_exception_{timestamp}.json'
        os.makedirs('results', exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)

        print(f'❌ 测试出错: {e}')
        print(f'💾 错误信息已保存到: {filename}')
        return error_result

def main():
    """主函数：运行所有四种认知压力条件的完整50题测评"""
    print('🧠 完整50题IPIP-FFM认知压力测评系统')
    print('=' * 100)

    # 四种认知压力条件配置
    test_conditions = [
        {
            'name': '基线条件',
            'emotional_stress': 0,
            'cognitive_trap': '',
            'context_tokens': 0,
            'temperature': 0.6
        },
        {
            'name': '语义谬误干扰',
            'emotional_stress': 0,
            'cognitive_trap': 's',  # 语义谬误
            'context_tokens': 400,
            'temperature': 0.6
        },
        {
            'name': '悖论陷阱干扰',
            'emotional_stress': 0,
            'cognitive_trap': 'p',  # 悖论陷阱
            'context_tokens': 400,
            'temperature': 0.6
        },
        {
            'name': '循环论证干扰',
            'emotional_stress': 0,
            'cognitive_trap': 'c',  # 循环论证
            'context_tokens': 800,
            'temperature': 0.6
        }
    ]

    all_results = []
    start_time = datetime.now()

    # 运行所有测试
    for i, condition in enumerate(test_conditions, 1):
        print(f'\n📍 第{i}/{len(test_conditions)}个条件: {condition["name"]}')
        print('=' * 100)

        result = run_complete_50_question_test(**condition)
        all_results.append(result)

        # 在测试之间稍作停顿，避免API限制
        if i < len(test_conditions):
            print(f'⏱️ 等待10秒后继续下一个测试...')
            time.sleep(10)

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # 生成总结报告
    print(f'\n📊 完整50题测评总结报告')
    print('=' * 100)
    print(f'总用时: {total_duration:.1f} 秒')
    print(f'测试条件数: {len(test_conditions)}')
    print(f'总题目数: {len(test_conditions) * 50}')

    successful_tests = sum(1 for r in all_results if r.get('success', False))
    print(f'成功测试: {successful_tests}/{len(test_conditions)}')

    # 保存总结报告
    summary_report = {
        'test_summary': {
            'total_conditions': len(test_conditions),
            'total_questions': len(test_conditions) * 50,
            'successful_tests': successful_tests,
            'total_duration_seconds': total_duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        },
        'conditions': test_conditions,
        'all_results': all_results,
        'summary_timestamp': datetime.now().isoformat()
    }

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_filename = f'results/complete_50_summary_report_{timestamp}.json'

    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, ensure_ascii=False, indent=2)

    print(f'💾 总结报告已保存到: {summary_filename}')
    print(f'🎉 所有完整50题测评完成！')

if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) > 1:
        condition_name = sys.argv[1]

        # 单个条件测试
        condition_map = {
            'baseline': ('基线条件', 0, '', 0),
            'semantic': ('语义谬误干扰', 0, 's', 400),
            'paradox': ('悖论陷阱干扰', 0, 'p', 400),
            'circular': ('循环论证干扰', 0, 'c', 800)
        }

        if condition_name.lower() in condition_map:
            name, stress, trap, tokens = condition_map[condition_name.lower()]
            run_complete_50_question_test(name, stress, trap, tokens)
        else:
            print(f'❌ 未知条件: {condition_name}')
            print('可用条件: baseline, semantic, paradox, circular')
    else:
        # 运行所有测试
        main()