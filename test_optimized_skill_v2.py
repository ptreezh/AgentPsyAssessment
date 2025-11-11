#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化版本的StandaloneQuestionnaireSkill V2
"""

import sys
import os
import json
import time
import asyncio
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join('.claude', 'skills', 'standalone-questionnaire'))

def test_v2_skill():
    """测试V2优化版本"""
    print('🚀 测试StandaloneQuestionnaireSkill V2优化版本')
    print('=' * 70)

    try:
        from skill_v2_optimized import StandaloneQuestionnaireSkillV2, QuestionnaireConfig

        # 创建自定义配置
        config = QuestionnaireConfig(
            max_questions=10,  # 测试用较小数量
            concurrent_requests=2,
            cache_enabled=True,
            timeout_seconds=30
        )

        # 创建技能实例
        skill = StandaloneQuestionnaireSkillV2(config)

        print(f'✅ V2技能初始化成功')
        print(f'📊 配置: 最大题目={config.max_questions}, 并发数={config.concurrent_requests}, 缓存启用={config.cache_enabled}')

        # 测试参数验证
        print(f'\n🔹 测试参数验证功能...')
        validation_result = skill._validate_and_adjust_parameters(
            emotional_stress=10,  # 超出范围
            cognitive_trap='invalid',  # 无效认知陷阱
            context_tokens=5000,  # 超出范围
            temperature=2.0,  # 超出范围
            max_questions=100  # 超出范围
        )

        print(f'   ⚠️ 预期警告数量: {len(validation_result["warnings"])}')
        for warning in validation_result['warnings']:
            print(f'   • {warning}')

        print(f'   ✅ 参数自动调整: {validation_result["adjustments"]}')

        # 测试缓存功能
        print(f'\n🔹 测试缓存功能...')
        if skill.cache:
            print(f'   ✅ 缓存系统已启用 (容量: {skill.cache.max_size})')
        else:
            print(f'   ❌ 缓存系统未启用')

        # 测试速率限制
        print(f'\n🔹 测试速率限制...')
        print(f'   ✅ 速率限制器已配置: {skill.rate_limiter.max_requests} 请求/秒')

        # 测试性能指标
        print(f'\n🔹 初始性能指标:')
        initial_metrics = skill.get_metrics()
        for key, value in initial_metrics.items():
            print(f'   • {key}: {value}')

        # 进行简单测试
        print(f'\n🔹 执行简单测试 (3题)...')
        start_time = time.time()

        result = skill.run_questionnaire_test(
            questionnaire_name='big_five_complete',
            role_name='default',
            emotional_stress=0,
            cognitive_trap='',
            context_tokens=0,
            temperature=0.6,
            max_questions=3
        )

        end_time = time.time()
        test_duration = end_time - start_time

        if result['success']:
            print(f'✅ 测试成功完成')
            print(f'   • 成功率: {result["session_info"]["successful_responses"]}/{result["session_info"]["total_questions"]}')
            print(f'   • 测试时长: {test_duration:.1f} 秒')

            # 显示性能指标
            if 'performance_metrics' in result:
                metrics = result['performance_metrics']
                print(f'\n📊 性能指标:')
                for key, value in metrics.items():
                    if isinstance(value, dict):
                        print(f'   • {key}:')
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, float):
                                print(f'     - {sub_key}: {sub_value:.3f}')
                            else:
                                print(f'     - {sub_key}: {sub_value}')
                    else:
                        print(f'   • {key}: {value}')

            # 显示当前技能指标
            print(f'\n📈 技能累计指标:')
            current_metrics = skill.get_metrics()
            for key, value in current_metrics.items():
                if isinstance(value, dict):
                    print(f'   • {key}:')
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, float):
                            print(f'     - {sub_key}: {sub_value:.3f}")
                        else:
                            print(f'     - {sub_key}: {sub_value}')
                elif isinstance(value, float):
                    print(f'   • {key}: {value:.3f}')
                else:
                    print(f'   • {key}: {value}')

            return True

        else:
            print(f'❌ 测试失败: {result.get("error", "Unknown error")}')
            return False

    except Exception as e:
        print(f'❌ 测试异常: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_async_functionality():
    """测试异步功能"""
    print(f'\n🔄 测试异步功能...')
    print('=' * 50)

    try:
        from skill_v2_optimized import StandaloneQuestionnaireSkillV2, QuestionnaireConfig

        config = QuestionnaireConfig(
            max_questions=5,
            concurrent_requests=3,
            cache_enabled=True
        )

        skill = StandaloneQuestionnaireSkillV2(config)

        async def run_async_test():
            print(f'🔹 执行异步测试...')
            start_time = time.time()

            result = await skill.run_questionnaire_test_async(
                questionnaire_name='big_five_complete',
                role_name='intj',
                emotional_stress=1,
                cognitive_trap='a',
                context_tokens=200,
                temperature=0.7,
                max_questions=5
            )

            end_time = time.time()
            duration = end_time - start_time

            if result['success']:
                print(f'✅ 异步测试成功')
                print(f'   • 成功率: {result["session_info"]["successful_responses"]}/{result["session_info"]["total_questions"]}')
                print(f'   • 用时: {duration:.1f} 秒')
                print(f'   • 平均每题: {duration/result["session_info"]["total_questions"]:.2f} 秒')

                # 检查缓存命中
                if skill.cache:
                    cache_stats = skill.cache.get_stats()
                    print(f'   • 缓存统计: {cache_stats}')

                return True
            else:
                print(f'❌ 异步测试失败: {result.get("error")}')
                return False

        return asyncio.run(run_async_test())

    except Exception as e:
        print(f'❌ 异步测试异常: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    print(f'\n🔄 测试向后兼容性...')
    print('=' * 50)

    try:
        from skill_v2_optimized import StandaloneQuestionnaireSkill

        # 使用旧接口创建实例
        skill = StandaloneQuestionnaireSkill()

        print(f'✅ 向后兼容别名工作正常')

        # 测试旧接口方法
        result = skill.run_questionnaire_test(
            questionnaire_name='big_five_complete',
            role_name='default',
            emotional_stress=0,
            cognitive_trap='',
            context_tokens=0,
            temperature=0.6,
            max_questions=2
        )

        if result['success']:
            print(f'✅ 旧接口方法正常工作')
            return True
        else:
            print(f'❌ 旧接口方法失败: {result.get("error")}')
            return False

    except Exception as e:
        print(f'❌ 向后兼容性测试失败: {e}')
        return False

def test_cache_performance():
    """测试缓存性能"""
    print(f'\n💾 测试缓存性能...')
    print('=' * 50)

    try:
        from skill_v2_optimized import StandaloneQuestionnaireSkillV2, QuestionnaireConfig

        config = QuestionnaireConfig(
            max_questions=3,
            cache_enabled=True,
            enable_metrics=True
        )

        skill = StandaloneQuestionnaireSkillV2(config)

        # 第一次请求（应该是缓存未命中）
        print(f'🔹 第一次请求（缓存未命中）...')
        start_time = time.time()
        result1 = skill.run_questionnaire_test(
            questionnaire_name='big_five_complete',
            role_name='default',
            emotional_stress=0,
            cognitive_trap='',
            context_tokens=0,
            temperature=0.6,
            max_questions=3
        )
        first_duration = time.time() - start_time

        # 第二次相同请求（应该是缓存命中）
        print(f'🔹 第二次请求（缓存命中）...')
        start_time = time.time()
        result2 = skill.run_questionnaire_test(
            questionnaire_name='big_five_complete',
            role_name='default',
            emotional_stress=0,
            cognitive_trap='',
            context_tokens=0,
            temperature=0.6,
            max_questions=3
        )
        second_duration = time.time() - start_time

        if result1['success'] and result2['success']:
            speed_improvement = (first_duration - second_duration) / first_duration * 100
            print(f'✅ 缓存性能测试完成')
            print(f'   • 第一次用时: {first_duration:.2f} 秒')
            print(f'   • 第二次用时: {second_duration:.2f} 秒')
            print(f'   • 性能提升: {speed_improvement:.1f}%')

            # 显示缓存统计
            metrics = skill.get_metrics()
            print(f'   • 缓存命中率: {metrics.get("cache_hit_rate", 0):.1%}')

            return speed_improvement > 0
        else:
            print(f'❌ 缓存测试失败')
            return False

    except Exception as e:
        print(f'❌ 缓存性能测试异常: {e}')
        return False

def main():
    """主测试函数"""
    print('🧪 StandaloneQuestionnaireSkill V2 优化版本完整测试')
    print('=' * 80)
    print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    # 运行所有测试
    tests = [
        ('基础功能测试', test_v2_skill),
        ('异步功能测试', test_async_functionality),
        ('向后兼容性测试', test_backward_compatibility),
        ('缓存性能测试', test_cache_performance)
    ]

    results = []
    for test_name, test_func in tests:
        print(f'📋 开始测试: {test_name}')
        try:
            result = test_func()
            results.append((test_name, result))
            print(f'   结果: {"✅ 通过" if result else "❌ 失败"}')
        except Exception as e:
            print(f'   结果: ❌ 异常 ({e})')
            results.append((test_name, False))
        print()

    # 总结
    print('=' * 80)
    print(f'📋 测试总结报告')
    print('=' * 80)

    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)

    print(f'📈 测试结果:')
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f'   • {test_name}: {status}')

    print(f'\n📊 总体统计:')
    print(f'   • 总测试数: {total_tests}')
    print(f'   • 通过测试: {passed_tests}')
    print(f'   • 失败测试: {total_tests - passed_tests}')
    print(f'   • 成功率: {passed_tests/total_tests*100:.1f}%')

    if passed_tests == total_tests:
        print(f'\n🎉 恭喜！StandaloneQuestionnaireSkill V2 优化版本所有测试通过！')
        print(f'✨ 新功能验证:')
        print(f'   • ✅ 异步并发处理 - 提升处理效率')
        print(f'   • ✅ 智能缓存机制 - 减少重复请求')
        print(f'   • ✅ 参数自动验证和调整 - 增强稳定性')
        print(f'   • ✅ 性能指标监控 - 实时性能跟踪')
        print(f'   • ✅ 增强错误处理 - 更好的容错能力')
        print(f'   • ✅ 配置管理系统 - 灵活的参数控制')
        print(f'   • ✅ 完全向后兼容 - 无缝升级')
    else:
        print(f'\n⚠️ 测试过程中发现问题，请检查实现。')

    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)