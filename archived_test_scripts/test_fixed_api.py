#!/usr/bin/env python3
"""
测试修复后的API调用问题
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join(os.path.dirname(__file__), '.claude', 'skills', 'standalone-questionnaire'))

from skill import StandaloneQuestionnaireSkill

def test_api_configuration():
    """测试API配置和简单调用"""

    print("🧪 测试修复后的独立问卷技能")
    print("=" * 60)

    # 创建技能实例
    questionnaire_skill = StandaloneQuestionnaireSkill()

    # 测试基线条件（简单测试）
    print("\n📋 测试条件: 基线条件 (简单测试)")
    print("描述: 正常状态，无压力干扰，只测试1题")
    print("-" * 50)

    try:
        # 运行问卷测试（只测试1题）
        result = questionnaire_skill.run_questionnaire_test(
            questionnaire_name="big_five_complete",
            role_name="default",
            emotional_stress=0,
            cognitive_trap="",
            context_tokens=0,
            temperature=0.6,
            max_questions=1
        )

        if result["success"]:
            print(f"✅ 问卷测试成功")
            print(f"📊 回答题目数: {len(result['answers'])}")
            print(f"📋 成功响应数: {result['session_info']['successful_responses']}")

            # 检查第一个回答
            if result['answers']:
                first_answer = result['answers'][0]
                response = first_answer.get('claude_response', '')

                if response.startswith('API Error'):
                    print(f"❌ API调用失败: {response}")
                    return False
                else:
                    print(f"✅ 成功获得Claude响应")
                    print(f"📝 响应长度: {len(response)} 字符")
                    print(f"🔍 响应预览: {response[:200]}...")

        else:
            print(f"❌ 问卷测试失败: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def test_moderate_pressure():
    """测试中等压力条件"""

    print("\n📋 测试条件: 中等压力条件")
    print("描述: 轻微情绪压力 + 简单认知陷阱")
    print("-" * 50)

    questionnaire_skill = StandaloneQuestionnaireSkill()

    try:
        # 运行问卷测试（只测试1题）
        result = questionnaire_skill.run_questionnaire_test(
            questionnaire_name="big_five_complete",
            role_name="default",
            emotional_stress=1,  # 轻微压力
            cognitive_trap="p",  # 悖论陷阱
            context_tokens=100,  # 轻微上下文
            temperature=0.8,
            max_questions=1
        )

        if result["success"]:
            print(f"✅ 中等压力测试成功")
            print(f"📊 回答题目数: {len(result['answers'])}")
            print(f"📋 成功响应数: {result['session_info']['successful_responses']}")

            # 检查第一个回答
            if result['answers']:
                first_answer = result['answers'][0]
                response = first_answer.get('claude_response', '')

                if response.startswith('API Error'):
                    print(f"❌ API调用失败: {response}")
                    return False
                else:
                    print(f"✅ 中等压力下成功获得响应")
                    print(f"📝 响应长度: {len(response)} 字符")

        else:
            print(f"❌ 中等压力测试失败: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ 中等压力测试出错: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🔧 开始测试修复后的API调用")

    # 测试1: 基线条件
    baseline_success = test_api_configuration()

    if baseline_success:
        print("\n" + "="*60)
        # 测试2: 中等压力条件
        moderate_success = test_moderate_pressure()

        if moderate_success:
            print("\n🎉 所有测试通过！API配置正确")
            print("可以安全地进行高压条件测试")
        else:
            print("\n⚠️ 中等压力测试失败，但基线测试成功")
            print("建议检查压力参数配置")
    else:
        print("\n❌ 基线测试失败，需要检查API配置")
        print("请检查:")
        print("1. API密钥是否正确设置")
        print("2. API端点是否可访问")
        print("3. 模型名称是否匹配")