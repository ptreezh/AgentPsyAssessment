#!/usr/bin/env python3
"""
修复版心理测评分析器
正确使用心理测评评估技能分析大五人格压力测试数据
"""

import sys
import os
import json

# 添加技能路径
sys.path.append('.claude/skills/psychological-analyzer')

def analyze_with_psychological_skill(test_data: dict) -> dict:
    """使用心理测评技能分析测试数据"""
    try:
        from skill import PsychologicalAnalyzer

        # 创建心理测评技能实例
        skill = PsychologicalAnalyzer()

        # 提取答案数据
        answers = test_data.get('answers', [])
        session_info = test_data.get('session_info', {})

        if not answers:
            return {
                'success': False,
                'error': '没有找到答案数据'
            }

        # 启动评估会话 - 传递题目数量而不是完整数据
        total_questions = len(answers)
        session_result = skill.start_evaluation_session(total_questions)

        print(f"✅ 成功启动评估会话: {session_result['session_id']}")

        # 逐个评估每个问题
        all_results = []
        for i, answer in enumerate(answers):
            print(f"正在评估问题 {i+1}/{total_questions}: {answer.get('question_id', 'Unknown')}")

            # 提取问题数据
            question_data = answer.get('question_data', {})
            claude_response = answer.get('claude_response', '')

            if not question_data or not claude_response:
                print(f"  ⚠️ 跳过无效问题数据")
                continue

            # 评估单个问题
            try:
                result = skill.evaluate_single_question({
                    'question': question_data.get('question', ''),
                    'question_id': question_data.get('question_id', ''),
                    'dimension': question_data.get('dimension', ''),
                    'response': claude_response
                })

                if 'error' in result:
                    print(f"  ❌ 评估失败: {result.get('error', '未知错误')}")
                else:
                    all_results.append(result)
                    print(f"  ✅ 评估成功: {result.get('scores', {})}")

            except Exception as e:
                print(f"  ❌ 评估异常: {e}")
                import traceback
                traceback.print_exc()

        # 完成评估并生成完整报告
        final_result = skill.complete_evaluation()

        if 'error' in final_result:
            print(f"  ❌ 完成评估失败: {final_result.get('error', '未知错误')}")
            return {
                'success': False,
                'error': final_result.get('error', '评估失败')
            }

        # 检查返回结果结构
        print(f"  📋 完整评估报告键: {list(final_result.keys())}")

        # 添加压力测试相关信息
        final_result['stress_parameters'] = {
                'emotional_stress': session_info.get('emotional_stress', 0),
                'cognitive_trap': session_info.get('cognitive_trap', ''),
                'context_tokens': session_info.get('context_tokens', 0),
                'temperature': session_info.get('temperature', 0.6),
                'role': session_info.get('role', 'default')
            }

            return final_result
        else:
            return {
                'success': False,
                'error': final_result.get('error', '评估失败')
            }

    except ImportError as e:
        return {
            'success': False,
            'error': f'无法导入心理测评技能: {e}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'分析过程出错: {e}'
        }

def main():
    # 要分析的大五人格测试文件
    test_files = [
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214654.json',  # 基线
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214706.json',  # 轻度压力
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214717.json',  # 中度压力
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214728.json',  # 高度压力
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214812.json'   # 极度压力
    ]

    stress_conditions = ['基线', '轻度压力', '中度压力', '高度压力', '极度压力']

    print('🧠 使用修复版心理测评技能分析大五人格压力测试')
    print('=' * 60)

    results = []

    for file_path, condition in zip(test_files, stress_conditions):
        print(f'\n{condition}条件分析:')
        print('-' * 30)

        if not os.path.exists(file_path):
            print(f'❌ 文件不存在: {file_path}')
            continue

        try:
            # 读取测试数据
            with open(file_path, 'r', encoding='utf-8') as f:
                test_data = json.load(f)

            # 使用修复版心理测评技能分析
            analysis = analyze_with_psychological_skill(test_data)

            if analysis.get('success'):
                print(f'✅ 分析成功!')
                print(f'📊 总分: {analysis.get("total_score", 0)}/{analysis.get("max_possible_score", 0)}')
                print(f'📈 平均分: {analysis.get("average_score", 0):.1f}')

                # 显示大五人格分数
                big_five = analysis.get('big_five_traits', {})
                if big_five:
                    print(f'🎯 大五人格分数:')
                    print(f'  开放性(O): {big_five.get("openness", 0):.1f}')
                    print(f'  尽责性(C): {big_five.get("conscientiousness", 0):.1f}')
                    print(f'  外向性(E): {big_five.get("extraversion", 0):.1f}')
                    print(f'  宜人性(A): {big_five.get("agreeableness", 0):.1f}')
                    print(f'  神经质(N): {big_five.get("neuroticism", 0):.1f}')

                # 显示MBTI类型
                mbti = analysis.get('mbti_assessment', {})
                if mbti:
                    print(f'🎭 MBTI类型: {mbti.get("type", "Unknown")} ({mbti.get("description", "")})')
                    print(f'置信度: {mbti.get("confidence", 0):.1f}%')

                # 显示压力参数
                stress_params = analysis.get('stress_parameters', {})
                print(f'📋 压力参数: 情绪={stress_params.get("emotional_stress", 0)}, '
                      f'认知陷阱="{stress_params.get("cognitive_trap", "")}", '
                      f'上下文={stress_params.get("context_tokens", 0)}tokens')

                results.append({
                    'condition': condition,
                    'analysis': analysis,
                    'file_path': file_path
                })
            else:
                print(f'❌ 分析失败: {analysis.get("error", "未知错误")}')

        except Exception as e:
            print(f'❌ 处理失败: {e}')
            import traceback
            traceback.print_exc()

    # 对比分析
    if len(results) >= 2:
        print(f'\n📊 压力条件对比分析')
        print('=' * 60)
        print(f"{'条件':<12} {'总分':<8} {'平均分':<8} {'O':<6} {'C':<6} {'E':<6} {'A':<6} {'N':<6} {'MBTI':<8}")
        print('-' * 80)

        for result in results:
            analysis = result['analysis']
            total = analysis.get('total_score', 0)
            max_possible = analysis.get('max_possible_score', 1)
            avg = analysis.get('average_score', 0)

            big_five = analysis.get('big_five_traits', {})
            o = big_five.get('openness', 0)
            c = big_five.get('conscientiousness', 0)
            e = big_five.get('extraversion', 0)
            a = big_five.get('agreeableness', 0)
            n = big_five.get('neuroticism', 0)

            mbti = analysis.get('mbti_assessment', {})
            mbti_type = mbti.get('type', 'Unknown')

            print(f'{result["condition"]:<12} {total}/{max_possible:<7} {avg:<8.1f} '
                  f'{o:<6.1f} {c:<6.1f} {e:<6.1f} {a:<6.1f} {n:<6.1f} {mbti_type:<8}')

        # 趋势分析
        print(f'\n📈 压力影响趋势分析:')
        print('-' * 30)

        baseline_big_five = results[0]['analysis'].get('big_five_traits', {})
        for i, result in enumerate(results[1:], 1):
            current_big_five = result['analysis'].get('big_five_traits', {})
            changes = {}

            for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                baseline_val = baseline_big_five.get(trait, 5.0)
                current_val = current_big_five.get(trait, 5.0)
                change = current_val - baseline_val
                changes[trait] = change

            # 显示总体变化趋势
            positive_changes = sum(1 for v in changes.values() if v > 0.3)
            negative_changes = sum(1 for v in changes.values() if v < -0.3)

            if positive_changes > negative_changes:
                trend = '整体上升趋势'
            elif negative_changes > positive_changes:
                trend = '整体下降趋势'
            else:
                trend = '相对稳定'

            print(f'{result["condition"]}: {trend}')

    # 保存结果
    if results:
        output_file = 'results/big_five_fixed_psychological_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_time': '2025-11-09T22:50:00',
                'test_type': 'big_five_stress_fixed_psychological',
                'conditions_analyzed': len(results),
                'results': results
            }, f, ensure_ascii=False, indent=2)

        print(f'\n💾 修复版分析结果已保存至: {output_file}')

if __name__ == "__main__":
    main()