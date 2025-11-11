#!/usr/bin/env python3
"""
测试修复后的高压条件人格表现
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.claude', 'skills', 'standalone-questionnaire'))

from skill import StandaloneQuestionnaireSkill

def test_high_pressure_conditions():
    """测试高压条件下的大五人格表现"""

    print("🧠 测试修复后的高压条件人格表现")
    print("=" * 60)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 测试条件配置（基于之前失败的高压条件）
    test_conditions = [
        {
            "name": "基线条件",
            "emotional_stress": 0,
            "cognitive_trap": "",
            "context_tokens": 0,
            "temperature": 0.6,
            "description": "正常状态，无压力干扰",
            "max_questions": 3
        },
        {
            "name": "中等压力条件",
            "emotional_stress": 2,
            "cognitive_trap": "p",  # 悖论陷阱
            "context_tokens": 500,
            "temperature": 1.0,
            "description": "中等情绪压力 + 悖论陷阱 + 中等上下文干扰",
            "max_questions": 3
        },
        {
            "name": "高压条件",
            "emotional_stress": 3,
            "cognitive_trap": "p",  # 悖论陷阱 - 之前失败的配置
            "context_tokens": 1000,
            "temperature": 1.2,
            "description": "高情绪压力 + 悖论陷阱 + 高上下文干扰",
            "max_questions": 3
        }
    ]

    results = {}

    for i, condition in enumerate(test_conditions, 1):
        print(f"\n📋 测试条件 {i}: {condition['name']}")
        print(f"描述: {condition['description']}")
        print(f"参数: 情绪压力={condition['emotional_stress']}, 认知陷阱={condition['cognitive_trap']}, 上下文={condition['context_tokens']}tokens, 温度={condition['temperature']}")
        print("-" * 50)

        try:
            # 运行问卷测试
            result = questionnaire_skill.run_questionnaire_test(
                questionnaire_name="big_five_complete",
                role_name="default",
                emotional_stress=condition['emotional_stress'],
                cognitive_trap=condition['cognitive_trap'],
                context_tokens=condition['context_tokens'],
                temperature=condition['temperature'],
                max_questions=condition['max_questions']
            )

            if result["success"]:
                print(f"✅ 问卷测试成功")
                print(f"📊 回答题目数: {len(result['answers'])}")
                print(f"📋 成功响应数: {result['session_info']['successful_responses']}")

                # 检查API错误
                api_errors = 0
                successful_responses = 0
                for answer in result.get('answers', []):
                    response = answer.get('claude_response', '')
                    if 'API Error' in response:
                        api_errors += 1
                        print(f"⚠️ 发现API错误: {response[:100]}...")
                    else:
                        successful_responses += 1

                if api_errors == 0:
                    print(f"✅ 所有回答都成功生成，无API错误")
                else:
                    print(f"⚠️ 发现 {api_errors} 个API错误，{successful_responses} 个成功响应")

                # 保存结果
                results[condition['name']] = result

                # 保存到文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results/fixed_high_pressure_test_{condition['name']}_{timestamp}.json"

                # 确保results目录存在
                os.makedirs("results", exist_ok=True)

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print(f"💾 结果已保存到: {filename}")

            else:
                print(f"❌ 问卷测试失败: {result['error']}")

        except Exception as e:
            print(f"❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()

    # 生成对比报告
    print(f"\n📈 修复后高压条件测试结果对比")
    print("=" * 60)

    successful_tests = 0
    total_api_errors = 0

    for condition_name, result in results.items():
        session_info = result.get('session_info', {})
        successful_responses = session_info.get('successful_responses', 0)
        total_questions = session_info.get('total_questions', 0)

        # 计算API错误数
        api_errors = 0
        for answer in result.get('answers', []):
            if 'API Error' in answer.get('claude_response', ''):
                api_errors += 1

        total_api_errors += api_errors

        if successful_responses == total_questions and total_questions > 0:
            successful_tests += 1

        print(f"\n🔍 {condition_name}:")
        print(f"   成功率: {successful_responses}/{total_questions} ({successful_responses/total_questions*100:.1f}%)" if total_questions > 0 else "   成功率: 0%")
        print(f"   API错误数: {api_errors}")
        print(f"   情绪压力: {session_info.get('emotional_stress', 'N/A')}")
        print(f"   认知陷阱: {session_info.get('cognitive_trap', 'N/A')}")
        print(f"   温度: {session_info.get('temperature', 'N/A')}")
        print(f"   测试时长: {session_info.get('start_time', 'N/A')} - {session_info.get('end_time', 'N/A')}")

    # 保存完整结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_file = f"results/fixed_high_pressure_comparison_{timestamp}.json"

    comparison_result = {
        "test_time": datetime.now().isoformat(),
        "test_type": "fixed_high_pressure_personality_comparison",
        "api_fixes_applied": [
            "Added retry mechanism with exponential backoff",
            "Enhanced error handling and logging",
            "Fixed model name for different API endpoints",
            "Added API configuration detection",
            "Increased interval time between calls"
        ],
        "conditions": [cond['name'] for cond in test_conditions],
        "results": results,
        "summary": {
            "total_conditions": len(test_conditions),
            "successful_tests": successful_tests,
            "total_api_errors": total_api_errors,
            "success_rate": f"{successful_tests/len(test_conditions)*100:.1f}%",
            "fix_status": "SUCCESS" if total_api_errors == 0 else "PARTIAL"
        }
    }

    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 对比结果已保存到: {comparison_file}")
    print(f"📊 总体成功率: {successful_tests}/{len(test_conditions)} ({successful_tests/len(test_conditions)*100:.1f}%)")
    print(f"🔧 总API错误数: {total_api_errors}")

    if total_api_errors == 0:
        print("🎉 高压条件测试完全成功！API问题已完全解决！")
    else:
        print(f"⚠️ 测试基本成功，但仍有 {total_api_errors} 个API错误需要进一步优化")

    print("\n✅ 修复总结:")
    print("1. ✅ 实现了指数退避重试机制")
    print("2. ✅ 增强了错误处理和诊断")
    print("3. ✅ 修复了不同API端点的模型名称匹配")
    print("4. ✅ 添加了API配置自动检测")
    print("5. ✅ 保持了API调用间隔")

    return comparison_result

if __name__ == "__main__":
    test_high_pressure_conditions()