#!/usr/bin/env python3
"""
重新测试高压条件下的大五人格表现
调整参数以避免API错误，使用更稳定的压力配置
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.claude', 'skills', 'standalone-questionnaire'))
sys.path.append(os.path.join(os.path.dirname(__file__), '.claude', 'skills', 'personality-assessor'))

from skill import StandaloneQuestionnaireSkill

def test_high_pressure_personality():
    """测试高压条件下的大五人格表现"""

    print("🧠 重新测试高压条件下的大五人格表现")
    print("=" * 60)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 测试条件配置（调整参数避免API错误）
    test_conditions = [
        {
            "name": "基线条件",
            "emotional_stress": 0,
            "cognitive_trap": "",
            "context_tokens": 0,
            "temperature": 0.6,
            "description": "正常状态，无压力干扰"
        },
        {
            "name": "中等压力条件",
            "emotional_stress": 2,
            "cognitive_trap": "a",  # 可得性启发 - 相对温和
            "context_tokens": 500,
            "temperature": 0.9,
            "description": "轻微情绪压力 + 可得性启发 + 轻度上下文干扰"
        },
        {
            "name": "高压条件",
            "emotional_stress": 3,
            "cognitive_trap": "s",  # 锚定效应 - 不会过于复杂
            "context_tokens": 800,
            "temperature": 1.1,
            "description": "中等情绪压力 + 锚定效应 + 中等上下文干扰"
        }
    ]

    results = {}

    for i, condition in enumerate(test_conditions, 1):
        print(f"\n📋 测试条件 {i}: {condition['name']}")
        print(f"描述: {condition['description']}")
        print(f"参数: 情绪压力={condition['emotional_stress']}, 认知陷阱={condition['cognitive_trap']}, 上下文={condition['context_tokens']}tokens, 温度={condition['temperature']}")
        print("-" * 50)

        try:
            # 运行问卷测试（限制为8题以确保稳定性）
            result = questionnaire_skill.run_questionnaire_test(
                questionnaire_name="big_five_complete",
                role_name="default",
                emotional_stress=condition['emotional_stress'],
                cognitive_trap=condition['cognitive_trap'],
                context_tokens=condition['context_tokens'],
                temperature=condition['temperature'],
                max_questions=8
            )

            if result["success"]:
                print(f"✅ 问卷测试成功")
                print(f"📊 回答题目数: {len(result['answers'])}")
                print(f"📋 成功响应数: {result['session_info']['successful_responses']}")

                # 检查是否有API错误
                api_errors = 0
                for answer in result.get('answers', []):
                    if 'API Error' in answer.get('claude_response', ''):
                        api_errors += 1

                if api_errors > 0:
                    print(f"⚠️ 发现 {api_errors} 个API错误")
                else:
                    print(f"✅ 所有回答都成功生成")

                # 保存结果
                results[condition['name']] = result

                # 保存到文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results/high_pressure_test_{condition['name']}_{timestamp}.json"

                # 确保results目录存在
                os.makedirs("results", exist_ok=True)

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print(f"💾 结果已保存到: {filename}")

            else:
                print(f"❌ 问卷测试失败")

        except Exception as e:
            print(f"❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()

    # 生成对比报告
    print(f"\n📈 高压条件测试结果对比")
    print("=" * 60)

    successful_tests = 0
    for condition_name, result in results.items():
        session_info = result.get('session_info', {})
        successful_responses = session_info.get('successful_responses', 0)
        total_questions = session_info.get('total_questions', 0)

        if successful_responses == total_questions and total_questions > 0:
            successful_tests += 1

        print(f"\n🔍 {condition_name}:")
        print(f"   成功率: {successful_responses}/{total_questions}")
        print(f"   情绪压力: {session_info.get('emotional_stress', 'N/A')}")
        print(f"   认知陷阱: {session_info.get('cognitive_trap', 'N/A')}")
        print(f"   温度: {session_info.get('temperature', 'N/A')}")
        print(f"   测试时长: {session_info.get('start_time', 'N/A')} - {session_info.get('end_time', 'N/A')}")

    # 保存完整结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_file = f"results/high_pressure_comparison_{timestamp}.json"

    comparison_result = {
        "test_time": datetime.now().isoformat(),
        "test_type": "high_pressure_personality_comparison",
        "conditions": [cond['name'] for cond in test_conditions],
        "results": results,
        "summary": {
            "total_conditions": len(test_conditions),
            "successful_tests": successful_tests,
            "success_rate": f"{successful_tests/len(test_conditions)*100:.1f}%"
        }
    }

    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 对比结果已保存到: {comparison_file}")
    print(f"📊 总体成功率: {successful_tests}/{len(test_conditions)} ({successful_tests/len(test_conditions)*100:.1f}%)")
    print("\n🎉 高压条件下的大五人格测试完成！")

    return comparison_result

if __name__ == "__main__":
    test_high_pressure_personality()