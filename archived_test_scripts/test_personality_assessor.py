#!/usr/bin/env python3
"""
测试人格评估技能
使用新创建的personality-assessor技能分析大五人格压力测试数据
"""

import sys
import os
import json

# 添加技能路径
sys.path.append('.claude/skills/personality-assessor')

def test_personality_assessor():
    """测试人格评估技能"""
    try:
        from skill import analyze_big_five_questionnaire

        # 要分析的大五人格测试文件
        test_files = [
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214654.json',  # 基线
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214706.json',  # 轻度压力
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214717.json',  # 中度压力
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214728.json',  # 高度压力
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214812.json'   # 极度压力
        ]

        stress_conditions = ['基线', '轻度压力', '中度压力', '高度压力', '极度压力']

        print('🧠 使用人格评估技能分析大五人格压力测试')
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

                # 使用人格评估技能分析
                analysis = analyze_big_five_questionnaire(test_data)

                if analysis.get('success'):
                    print(f'✅ 分析成功!')

                    # 显示会话信息
                    session_info = analysis.get('session_info', {})
                    print(f'📋 会话ID: {session_info.get("session_id", "Unknown")}')
                    print(f'📊 成功评估题目: {session_info.get("successful_evaluations", 0)}/{session_info.get("total_questions", 0)}')

                    # 显示大五人格分数
                    big_five = analysis.get('big_five_scores', {})
                    if big_five:
                        print(f'🎯 大五人格分数:')
                        print(f'  开放性(O): {big_five.get("O", 0):.2f}')
                        print(f'  尽责性(C): {big_five.get("C", 0):.2f}')
                        print(f'  外向性(E): {big_five.get("E", 0):.2f}')
                        print(f'  宜人性(A): {big_five.get("A", 0):.2f}')
                        print(f'  神经质(N): {big_five.get("N", 0):.2f}')

                    # 显示MBTI类型
                    mbti = analysis.get('mbti_assessment', {})
                    if mbti:
                        print(f'🎭 MBTI类型: {mbti.get("type", "Unknown")} ({mbti.get("description", "")})')
                        print(f'置信度: {mbti.get("confidence", 0):.1f}%')

                    # 显示贝尔宾团队角色
                    belbin = analysis.get('belbin_assessment', {})
                    if belbin:
                        print(f'👥 贝尔宾角色: {belbin.get("primary_role", "Unknown")}')
                        print(f'匹配度: {belbin.get("match_score", 0):.1f}%')
                        print(f'描述: {belbin.get("description", "")}')

                    # 显示评估置信度
                    confidence = analysis.get('evaluation_confidence', 0)
                    print(f'📈 评估置信度: {confidence:.1f}%')

                    # 显示压力参数
                    session_data = test_data.get('session_info', {})
                    print(f'📋 压力参数: 情绪={session_data.get("emotional_stress", 0)}, '
                          f'认知陷阱="{session_data.get("cognitive_trap", "")}", '
                          f'上下文={session_data.get("context_tokens", 0)}tokens')

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
            print('=' * 80)
            print(f"{'条件':<12} {'O':<6} {'C':<6} {'E':<6} {'A':<6} {'N':<6} {'MBTI':<8} {'置信度':<8} {'贝尔宾':<12}")
            print('-' * 90)

            for result in results:
                analysis = result['analysis']
                big_five = analysis.get('big_five_scores', {})
                o = big_five.get('O', 0)
                c = big_five.get('C', 0)
                e = big_five.get('E', 0)
                a = big_five.get('A', 0)
                n = big_five.get('N', 0)

                mbti = analysis.get('mbti_assessment', {})
                mbti_type = mbti.get('type', 'Unknown')
                mbti_conf = mbti.get('confidence', 0)

                belbin = analysis.get('belbin_assessment', {})
                belbin_role = belbin.get('primary_role', 'Unknown')[:8]  # 截取前8个字符

                print(f'{result["condition"]:<12} '
                      f'{o:<6.2f} {c:<6.2f} {e:<6.2f} {a:<6.2f} {n:<6.2f} '
                      f'{mbti_type:<8} {mbti_conf:<8.1f} {belbin_role:<12}')

            # 趋势分析
            print(f'\n📈 压力影响趋势分析:')
            print('-' * 30)

            baseline_big_five = results[0]['analysis'].get('big_five_scores', {})
            for i, result in enumerate(results[1:], 1):
                current_big_five = result['analysis'].get('big_five_scores', {})
                changes = {}

                for trait in ['O', 'C', 'E', 'A', 'N']:
                    baseline_val = baseline_big_five.get(trait, 3.0)
                    current_val = current_big_five.get(trait, 3.0)
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

                # 显示关键变化
                trait_names = {
                    'O': '开放性',
                    'C': '尽责性',
                    'E': '外向性',
                    'A': '宜人性',
                    'N': '神经质'
                }

                print(f'  详细变化:')
                for trait, change in changes.items():
                    if abs(change) > 0.1:
                        trend = '↑' if change > 0 else '↓'
                        baseline_val = baseline_big_five.get(trait, 3.0)
                        current_val = current_big_five.get(trait, 3.0)
                        print(f'    {trait_names[trait]}: {baseline_val:.2f} → {current_val:.2f} ({trend} {change:+.2f})')

            # MBTI类型变化
            print(f'\n🎭 MBTI类型变化:')
            print('-' * 20)
            for result in results:
                mbti = result['analysis'].get('mbti_assessment', {})
                belbin = result['analysis'].get('belbin_assessment', {})
                print(f'{result["condition"]}: {mbti.get("type", "Unknown")} (置信度: {mbti.get("confidence", 0):.1f}%) - {belbin.get("primary_role", "Unknown")}')

        # 保存结果
        if results:
            output_file = 'results/big_five_personality_assessor_analysis.json'
            os.makedirs('results', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'analysis_time': '2025-11-09T22:20:00',
                    'test_type': 'big_five_stress_personality_assessor',
                    'conditions_analyzed': len(results),
                    'results': results
                }, f, ensure_ascii=False, indent=2)

            print(f'\n💾 人格评估分析结果已保存至: {output_file}')
            print(f'\n✅ 成功使用人格评估技能完成大五人格压力测试分析！')

    except ImportError as e:
        print(f'❌ 无法导入人格评估技能: {e}')
    except Exception as e:
        print(f'❌ 测试过程出错: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_personality_assessor()