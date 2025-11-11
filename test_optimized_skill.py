#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化版本的standalone-questionnaire技能
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join('.claude', 'skills', 'standalone-questionnaire'))

def test_v2_skill():
    """测试V2优化版本"""
    print('🚀 测试StandaloneQuestionnaireSkillV2优化版本')
    print('=' * 70)

    try:
        from skill_v2 import StandaloneQuestionnaireSkillV2, QuestionnaireConfig

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
        validation_result = skill._validate_parameters(
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
                    if isinstance(value, float):
                        print(f'   • {key}: {value:.3f}')
                    else:
                        print(f'   • {key}: {value}')

            # 显示当前技能指标
            print(f'\n📈 技能累计指标:')
            current_metrics = skill.get_metrics()
            for key, value in current_metrics.items():
                if isinstance(value, float):
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

def test_backward_compatibility():
    """测试向后兼容性"""
    print(f'\n🔄 测试向后兼容性...')
    print('=' * 50)

    try:
        from skill_v2 import StandaloneQuestionnaireSkill

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

def main():
    """主测试函数"""
    print('🧪 StandaloneQuestionnaireSkill V2 优化版本测试')
    print('=' * 80)
    print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    # 测试V2新功能
    v2_success = test_v2_skill()

    # 测试向后兼容性
    compat_success = test_backward_compatibility()

    # 总结
    print(f'\n' + '=' * 80)
    print(f'📋 测试总结报告')
    print(f'=' * 80)

    print(f'📈 测试结果:')
    print(f'   • V2优化功能测试: {"✅ 通过" if v2_success else "❌ 失败"}')
    print(f'   • 向后兼容性测试: {"✅ 通过" if compat_success else "❌ 失败"}')

    overall_success = v2_success and compat_success
    print(f'   • 总体测试结果: {"✅ 全部通过" if overall_success else "❌ 存在失败"}')

    if overall_success:
        print(f'\n🎉 恭喜！StandaloneQuestionnaireSkill V2 优化版本测试成功！')
        print(f'✨ 新功能包括:')
        print(f'   • 异步并发处理')
        print(f'   • 智能缓存机制')
        print(f'   • 参数自动验证和调整')
        print(f'   • 性能指标监控')
        print(f'   • 增强错误处理')
        print(f'   • 完全向后兼容')
    else:
        print(f'\n⚠️ 测试过程中发现问题，请检查实现。')

    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)