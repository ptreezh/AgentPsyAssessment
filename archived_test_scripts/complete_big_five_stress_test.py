#!/usr/bin/env python3
"""
完整的大五人格压力测试流程
1. 使用问卷测评技能在不同压力条件下生成答卷
2. 使用人格评估技能对这些答卷进行专业分析
"""

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append('.claude/skills/standalone-questionnaire')
sys.path.append('.claude/skills/personality-assessor')

def generate_questionnaire_responses():
    """第一步：使用问卷测评技能生成不同压力条件下的答卷"""
    try:
        from skill import StandaloneQuestionnaireSkill

        # 创建问卷测评技能实例
        questionnaire_skill = StandaloneQuestionnaireSkill()

        # 定义压力条件
        stress_conditions = [
            {'name': '基线', 'emotional_stress': 0, 'cognitive_trap': '', 'context_tokens': 0},
            {'name': '轻度压力', 'emotional_stress': 1, 'cognitive_trap': 'p', 'context_tokens': 500},
            {'name': '中度压力', 'emotional_stress': 2, 'cognitive_trap': 'c', 'context_tokens': 1000},
            {'name': '高度压力', 'emotional_stress': 3, 'cognitive_trap': 's', 'context_tokens': 2000},
            {'name': '极度压力', 'emotional_stress': 4, 'cognitive_trap': 'r', 'context_tokens': 3000}
        ]

        print('🎯 第一步：生成不同压力条件下的大五人格问卷答卷')
        print('=' * 60)

        generated_files = []

        for stress_config in stress_conditions:
            print(f'\n正在生成 {stress_config["name"]} 条件的答卷...')
            print('-' * 40)

            # 生成答卷
            result = questionnaire_skill.run_questionnaire_test(
                questionnaire_name='big_five_short',
                role_name='default',
                emotional_stress=stress_config['emotional_stress'],
                cognitive_trap=stress_config['cognitive_trap'],
                context_tokens=stress_config['context_tokens']
            )

            if result.get('success'):
                print(f'✅ {stress_config["name"]} 答卷生成成功!')
                print(f'📊 题目数量: {len(result.get("answers", []))}')

                # 保存答卷数据
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'big_five_stress_fresh_{stress_config["name"]}_{timestamp}.json'
                filepath = f'results/{filename}'

                os.makedirs('results', exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        'generation_time': datetime.now().isoformat(),
                        'stress_condition': stress_config['name'],
                        'stress_config': stress_config,
                        'questionnaire_result': result
                    }, f, ensure_ascii=False, indent=2)

                generated_files.append({
                    'condition': stress_config['name'],
                    'config': stress_config,
                    'filepath': filepath,
                    'data': result
                })

                # 显示一些示例回答
                answers = result.get('answers', [])
                if answers:
                    print(f'📝 示例回答（前2题）:')
                    for i, answer in enumerate(answers[:2]):
                        print(f'  题目{i+1}: {answer.get("question_data", {}).get("question", "")[:50]}...')
                        print(f'  回答: {answer.get("claude_response", "")[:100]}...')
                        print()
            else:
                print(f'❌ {stress_config["name"]} 答卷生成失败: {result.get("error", "未知错误")}')

        return generated_files

    except ImportError as e:
        print(f'❌ 无法导入问卷测评技能: {e}')
        return []
    except Exception as e:
        print(f'❌ 生成答卷过程出错: {e}')
        import traceback
        traceback.print_exc()
        return []

def analyze_responses_with_personality_assessor(generated_files):
    """第二步：使用人格评估技能分析生成的答卷"""
    try:
        from skill import analyze_big_five_questionnaire

        print('\n\n🧠 第二步：使用人格评估技能分析答卷')
        print('=' * 60)

        analysis_results = []

        for file_info in generated_files:
            condition = file_info['condition']
            questionnaire_data = file_info['data']

            print(f'\n分析 {condition} 条件的答卷...')
            print('-' * 30)

            # 使用人格评估技能分析
            analysis = analyze_big_five_questionnaire(questionnaire_data)

            if analysis.get('success'):
                print(f'✅ {condition} 分析成功!')

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

                # 显示压力参数
                stress_config = file_info['config']
                print(f'📋 压力参数: 情绪={stress_config["emotional_stress"]}, '
                      f'认知陷阱="{stress_config["cognitive_trap"]}", '
                      f'上下文={stress_config["context_tokens"]}tokens')

                analysis_results.append({
                    'condition': condition,
                    'stress_config': stress_config,
                    'analysis': analysis,
                    'filepath': file_info['filepath']
                })
            else:
                print(f'❌ {condition} 分析失败: {analysis.get("error", "未知错误")}')

        return analysis_results

    except ImportError as e:
        print(f'❌ 无法导入人格评估技能: {e}')
        return []
    except Exception as e:
        print(f'❌ 分析过程出错: {e}')
        import traceback
        traceback.print_exc()
        return []

def generate_comprehensive_report(analysis_results):
    """生成综合分析报告"""
    if len(analysis_results) < 2:
        print('\n⚠️ 分析结果不足，无法生成对比报告')
        return

    print('\n\n📊 大五人格压力测试综合分析报告')
    print('=' * 80)
    print(f"{'条件':<12} {'O':<6} {'C':<6} {'E':<6} {'A':<6} {'N':<6} {'MBTI':<8} {'置信度':<8} {'贝尔宾':<12}")
    print('-' * 90)

    for result in analysis_results:
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
        belbin_role = belbin.get('primary_role', 'Unknown')[:10]

        print(f'{result["condition"]:<12} '
              f'{o:<6.2f} {c:<6.2f} {e:<6.2f} {a:<6.2f} {n:<6.2f} '
              f'{mbti_type:<8} {mbti_conf:<8.1f} {belbin_role:<12}')

    # 趋势分析
    print(f'\n📈 压力影响趋势分析:')
    print('-' * 30)

    baseline_result = analysis_results[0]
    baseline_big_five = baseline_result['analysis'].get('big_five_scores', {})

    for i, result in enumerate(analysis_results[1:], 1):
        current_big_five = result['analysis'].get('big_five_scores', {})
        changes = {}

        for trait in ['O', 'C', 'E', 'A', 'N']:
            baseline_val = baseline_big_five.get(trait, 3.0)
            current_val = current_big_five.get(trait, 3.0)
            change = current_val - baseline_val
            changes[trait] = change

        # 显示总体变化趋势
        positive_changes = sum(1 for v in changes.values() if v > 0.2)
        negative_changes = sum(1 for v in changes.values() if v < -0.2)

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

        significant_changes = []
        for trait, change in changes.items():
            if abs(change) > 0.1:
                baseline_val = baseline_big_five.get(trait, 3.0)
                current_val = current_big_five.get(trait, 3.0)
                trend_symbol = '↑' if change > 0 else '↓'
                significant_changes.append(f'{trait_names[trait]}: {baseline_val:.2f} → {current_val:.2f} ({trend_symbol} {change:+.2f})')

        if significant_changes:
            print(f'  显著变化: {", ".join(significant_changes)}')

    # MBTI类型变化
    print(f'\n🎭 MBTI类型变化路径:')
    print('-' * 25)
    for result in analysis_results:
        mbti = result['analysis'].get('mbti_assessment', {})
        belbin = result['analysis'].get('belbin_assessment', {})
        print(f'{result["condition"]}: {mbti.get("type", "Unknown")} (置信度: {mbti.get("confidence", 0):.1f}%) - {belbin.get("primary_role", "Unknown")}')

    # 保存综合报告
    output_file = f'results/big_five_stress_comprehensive_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_time': datetime.now().isoformat(),
            'test_type': 'big_five_stress_comprehensive',
            'conditions_tested': len(analysis_results),
            'workflow': ['questionnaire_generation', 'personality_assessment'],
            'results': analysis_results
        }, f, ensure_ascii=False, indent=2)

    print(f'\n💾 综合分析报告已保存至: {output_file}')
    print(f'\n✅ 完整的大五人格压力测试流程执行完成！')

def main():
    """主函数：执行完整的大五人格压力测试流程"""
    print('🚀 开始完整的大五人格压力测试流程')
    print('流程: 1️⃣ 问卷测评 → 2️⃣ 人格评估 → 3️⃣ 综合分析')
    print('=' * 80)

    # 第一步：生成答卷
    generated_files = generate_questionnaire_responses()

    if not generated_files:
        print('\n❌ 问卷生成失败，无法继续分析')
        return

    # 第二步：分析答卷
    analysis_results = analyze_responses_with_personality_assessor(generated_files)

    if not analysis_results:
        print('\n❌ 人格分析失败')
        return

    # 第三步：生成综合报告
    generate_comprehensive_report(analysis_results)

if __name__ == "__main__":
    main()