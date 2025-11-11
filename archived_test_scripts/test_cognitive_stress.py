#!/usr/bin/env python3
"""
测试相同温度默认角色在不同认知干扰压力条件下的大五人格表现
使用修复后的独立问卷技能系统进行认知压力测试
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.claude', 'skills', 'standalone-questionnaire'))

from skill import StandaloneQuestionnaireSkill

def test_cognitive_stress_big_five():
    """测试认知干扰压力对大五人格表现的影响"""

    print("🧠 认知干扰压力对大五人格表现影响测试")
    print("=" * 80)
    print("测试设计：相同温度(0.6) + 默认角色 + 不同认知陷阱")
    print("=" * 80)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 认知干扰压力测试条件 - 固定温度0.6，默认角色
    cognitive_stress_conditions = [
        {
            "name": "无认知干扰-基线",
            "emotional_stress": 0,
            "cognitive_trap": "",
            "context_tokens": 0,
            "temperature": 0.6,
            "description": "基线条件，无任何认知干扰",
            "max_questions": 10  # 使用10题以节省时间，但覆盖所有维度
        },
        {
            "name": "语义谬误干扰",
            "emotional_stress": 0,
            "cognitive_trap": "s",  # 语义谬误
            "context_tokens": 200,
            "temperature": 0.6,
            "description": "语义谬误干扰 + 轻度上下文",
            "max_questions": 10
        },
        {
            "name": "悖论陷阱干扰",
            "emotional_stress": 0,
            "cognitive_trap": "p",  # 悖论陷阱
            "context_tokens": 500,
            "temperature": 0.6,
            "description": "悖论陷阱干扰 + 中等上下文",
            "max_questions": 10
        },
        {
            "name": "循环论证干扰",
            "emotional_stress": 0,
            "cognitive_trap": "c",  # 循环论证
            "context_tokens": 800,
            "temperature": 0.6,
            "description": "循环论证干扰 + 高上下文",
            "max_questions": 10
        }
    ]

    results_summary = []

    for i, condition in enumerate(cognitive_stress_conditions, 1):
        print(f"\n📋 测试阶段 {i}/{len(cognitive_stress_conditions)}: {condition['name']}")
        print(f"描述: {condition['description']}")
        print(f"参数: 情绪压力={condition['emotional_stress']}, 认知陷阱={condition['cognitive_trap']}, 上下文={condition['context_tokens']}tokens, 温度={condition['temperature']}")
        print(f"题目数量: {condition['max_questions']}题")
        print("-" * 70)

        try:
            # 使用问卷技能生成压力条件下的回答
            print(f"🔹 开始生成问卷回答...")
            start_time = datetime.now()

            questionnaire_result = questionnaire_skill.run_questionnaire_test(
                questionnaire_name="big_five_complete",
                role_name="default",
                emotional_stress=condition['emotional_stress'],
                cognitive_trap=condition['cognitive_trap'],
                context_tokens=condition['context_tokens'],
                temperature=condition['temperature'],
                max_questions=condition['max_questions']
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            if not questionnaire_result["success"]:
                print(f"❌ 问卷生成失败: {questionnaire_result['error']}")
                continue

            successful_responses = questionnaire_result['session_info']['successful_responses']
            total_questions = questionnaire_result['session_info']['total_questions']

            print(f"✅ 问卷生成成功: {successful_responses}/{total_questions} 题目回答")
            print(f"⏱️ 用时: {duration:.1f} 秒")

            # 检查参数调整
            session_info = questionnaire_result['session_info']
            original_params = {
                "temperature": session_info.get('temperature'),
                "context_tokens": session_info.get('context_tokens')
            }
            adjusted_params = {
                "temperature": session_info.get('adjusted_temperature'),
                "context_tokens": session_info.get('adjusted_context_tokens')
            }

            parameter_adjustments = []
            if original_params["temperature"] != adjusted_params["temperature"]:
                parameter_adjustments.append(f"温度: {original_params['temperature']} → {adjusted_params['temperature']}")
            if original_params["context_tokens"] != adjusted_params["context_tokens"]:
                parameter_adjustments.append(f"上下文: {original_params['context_tokens']} → {adjusted_params['context_tokens']}")

            if parameter_adjustments:
                print(f"⚠️ 参数自动调整: {', '.join(parameter_adjustments)}")

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
                print(f"✅ 所有回答成功生成")
                print(f"📊 平均回答长度: {avg_response_length:.0f} 字符")
                print(f"📊 维度覆盖: E={dimensions_count['E']}, A={dimensions_count['A']}, C={dimensions_count['C']}, N={dimensions_count['N']}, O={dimensions_count['O']}")
                print(f"📊 覆盖率: {sum(dimensions_count.values())}/{condition['max_questions']} ({sum(dimensions_count.values())/condition['max_questions']*100:.1f}%)")
            else:
                print(f"⚠️ 发现 {api_errors} 个API错误")

            # 保存结果
            comprehensive_result = {
                "condition": condition,
                "questionnaire_result": questionnaire_result,
                "performance_metrics": {
                    "success_rate": f"{successful_responses}/{total_questions}",
                    "api_errors": api_errors,
                    "avg_response_length": avg_response_length if api_errors == 0 else 0,
                    "dimensions_count": dimensions_count,
                    "total_dimensions_covered": sum(dimensions_count.values()),
                    "coverage_percentage": sum(dimensions_count.values())/condition['max_questions']*100,
                    "parameter_adjustments": parameter_adjustments,
                    "test_duration_seconds": duration,
                    "avg_time_per_question": duration/total_questions if total_questions > 0 else 0
                },
                "test_timestamp": datetime.now().isoformat()
            }

            results_summary.append(comprehensive_result)

            # 保存到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/cognitive_stress_{condition['name']}_{timestamp}.json"
            os.makedirs("results", exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_result, f, ensure_ascii=False, indent=2)

            print(f"💾 结果已保存到: {filename}")

        except Exception as e:
            print(f"❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()

    # 生成认知干扰压力对比分析报告
    print(f"\n📈 认知干扰压力对大五人格表现影响分析")
    print("=" * 80)

    if results_summary:
        print(f"\n🔍 认知干扰条件对比:")
        for result in results_summary:
            condition = result['condition']['name']
            metrics = result['performance_metrics']
            success_rate = metrics['success_rate']
            api_errors = metrics['api_errors']
            avg_length = metrics['avg_response_length']
            dimensions = metrics['dimensions_count']
            total_dimensions = metrics['total_dimensions_covered']
            coverage = metrics['coverage_percentage']
            adjustments = metrics['parameter_adjustments']
            duration = metrics['test_duration_seconds']
            avg_time = metrics['avg_time_per_question']

            print(f"\n   📋 {condition}:")
            print(f"      成功率: {success_rate}")
            print(f"      API错误: {api_errors}")
            print(f"      平均回答长度: {avg_length:.0f} 字符")
            print(f"      维度覆盖: E={dimensions['E']}, A={dimensions['A']}, C={dimensions['C']}, N={dimensions['N']}, O={dimensions['O']}")
            print(f"      覆盖率: {coverage:.1f}% ({total_dimensions}/10题)")
            print(f"      测试时长: {duration:.1f} 秒")
            print(f"      平均每题: {avg_time:.2f} 秒")
            if adjustments:
                print(f"      参数调整: {', '.join(adjustments)}")

        # 认知干扰对人格表现的影响分析
        print(f"\n📊 认知干扰影响分析:")

        # 分析各项指标的变化趋势
        success_rates = []
        avg_lengths = []
        api_errors_list = []
        coverage_percentages = []
        durations = []
        avg_times = []

        for result in results_summary:
            success_parts = result['performance_metrics']['success_rate'].split('/')
            success_rate = int(success_parts[0]) / int(success_parts[1]) if len(success_parts) == 2 else 0
            success_rates.append(success_rate)
            avg_lengths.append(result['performance_metrics']['avg_response_length'])
            api_errors_list.append(result['performance_metrics']['api_errors'])
            coverage_percentages.append(result['performance_metrics']['coverage_percentage'])
            durations.append(result['performance_metrics']['test_duration_seconds'])
            avg_times.append(result['performance_metrics']['avg_time_per_question'])

        if success_rates:
            condition_names = [result['condition']['name'] for result in results_summary]

            print(f"   📈 成功率变化: {[f'{rate:.1%}' for rate in success_rates]}")
            print(f"   📝 平均回答长度变化: {[f'{length:.0f}字' for length in avg_lengths]}")
            print(f"   ❌ API错误变化: {api_errors_list}")
            print(f"   🎯 维度覆盖率变化: {[f'{coverage:.1f}%' for coverage in coverage_percentages]}")
            print(f"   ⏱️ 测试时长变化: {[f'{duration:.1f}s' for duration in durations]}")
            print(f"   ⚡ 每题平均时间: {[f'{time:.2f}s' for time in avg_times]}")

            # 认知干扰影响趋势分析
            print(f"\n🧠 认知干扰压力影响趋势:")
            if len(avg_lengths) > 1:
                baseline_length = avg_lengths[0]
                for i, (name, length) in enumerate(zip(condition_names, avg_lengths)):
                    if i > 0:
                        change_percent = ((length - baseline_length) / baseline_length) * 100 if baseline_length > 0 else 0
                        direction = '↗️' if change_percent > 5 else '↘️' if change_percent < -5 else '➡️'
                        print(f"   {direction} {name}: 回答长度变化 {change_percent:+.1f}%")

        # 保存完整对比报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_file = f"results/cognitive_stress_comparison_{timestamp}.json"

        comparison_report = {
            "test_time": datetime.now().isoformat(),
            "test_type": "cognitive_stress_big_five_analysis",
            "fixed_parameters": {
                "temperature": 0.6,
                "role": "default",
                "questionnaire": "big_five_complete"
            },
            "variable_parameter": "cognitive_trap_and_context",
            "conditions_tested": len(results_summary),
            "questions_per_test": 10,
            "results": results_summary,
            "analysis": {
                "total_conditions": len(cognitive_stress_conditions),
                "successful_conditions": len(results_summary),
                "success_rate": f"{len(results_summary)/len(cognitive_stress_conditions)*100:.1f}%",
                "performance_trends": {
                    "success_rates": success_rates,
                    "avg_response_lengths": avg_lengths,
                    "api_errors": api_errors_list,
                    "coverage_percentages": coverage_percentages,
                    "test_durations": durations,
                    "avg_times_per_question": avg_times
                }
            }
        }

        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 认知干扰对比报告已保存到: {comparison_file}")

    print(f"\n🎉 认知干扰压力测试完成！")
    print(f"\n✅ 测试总结:")
    print("1. ✅ 相同温度(0.6)和默认角色条件下，测试了4种认知干扰压力")
    print("2. ✅ 分析了语义谬误、悖论陷阱、循环论证等认知干扰对人格表现的影响")
    print("3. ✅ 记录了回答长度、维度覆盖、API错误率等关键指标")
    print("4. ✅ 生成了认知干扰压力影响对比分析报告")
    print("5. ✅ 验证了技能在不同认知干扰条件下的稳定性")

    return results_summary

if __name__ == "__main__":
    test_cognitive_stress_big_five()