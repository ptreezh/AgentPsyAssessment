#!/usr/bin/env python3
"""
测试参数调整后的API调用
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.claude', 'skills', 'standalone-questionnaire'))

from skill import StandaloneQuestionnaireSkill

def test_parameter_adjustment():
    """测试参数调整功能"""

    print("🔧 测试智谱API参数自动调整功能")
    print("=" * 60)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 测试不同参数组合
    test_cases = [
        {
            "name": "高温参数测试",
            "temperature": 1.5,  # 超出智谱API限制
            "context_tokens": 500,
            "expected_adjustment": True
        },
        {
            "name": "高超参数测试",
            "temperature": 2.5,  # 远超智谱API限制
            "context_tokens": 1200,  # 超出智谱API限制
            "expected_adjustment": True
        },
        {
            "name": "正常参数测试",
            "temperature": 0.8,  # 在限制范围内
            "context_tokens": 300,  # 在限制范围内
            "expected_adjustment": False
        }
    ]

    for test_case in test_cases:
        print(f"\n📋 测试案例: {test_case['name']}")
        print(f"原始参数: 温度={test_case['temperature']}, 上下文={test_case['context_tokens']}tokens")
        print("-" * 50)

        try:
            # 运行问卷测试（只测试1题）
            result = questionnaire_skill.run_questionnaire_test(
                questionnaire_name="big_five_complete",
                role_name="default",
                emotional_stress=1,  # 轻微压力
                cognitive_trap="",    # 无认知陷阱简化测试
                context_tokens=test_case['context_tokens'],
                temperature=test_case['temperature'],
                max_questions=1
            )

            if result["success"]:
                session_info = result.get('session_info', {})
                original_temp = session_info.get('temperature')
                adjusted_temp = session_info.get('adjusted_temperature')
                original_context = session_info.get('context_tokens')
                adjusted_context = session_info.get('adjusted_context_tokens')

                print(f"✅ 问卷测试成功")
                print(f"📊 温度调整: {original_temp} → {adjusted_temp}")
                print(f"📊 上下文调整: {original_context} → {adjusted_context}")

                # 检查是否有API错误
                api_errors = 0
                for answer in result.get('answers', []):
                    if 'API Error' in answer.get('claude_response', ''):
                        api_errors += 1

                if api_errors == 0:
                    print(f"✅ 无API错误，参数调整成功")

                    # 验证参数调整是否符合预期
                    if test_case['expected_adjustment']:
                        if adjusted_temp != original_temp or adjusted_context != original_context:
                            print(f"✅ 参数按预期调整")
                        else:
                            print(f"⚠️ 预期需要调整但参数未变化")
                    else:
                        if adjusted_temp == original_temp and adjusted_context == original_context:
                            print(f"✅ 参数保持原值，符合预期")
                        else:
                            print(f"⚠️ 预期不需要调整但参数发生了变化")
                else:
                    print(f"❌ 仍有 {api_errors} 个API错误")

            else:
                print(f"❌ 问卷测试失败: {result['error']}")

        except Exception as e:
            print(f"❌ 测试出错: {e}")

    print(f"\n🎉 参数调整测试完成")

if __name__ == "__main__":
    test_parameter_adjustment()