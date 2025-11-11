#!/usr/bin/env python3
"""
大五人格压力测试心理评估分析
使用心理测评评估技能分析不同压力条件下的大五人格表现
"""

import sys
import os
import json
from pathlib import Path

# 添加技能路径
sys.path.append('.claude/skills/psychological-analyzer')

def main():
    try:
        from skill import PsychologicalAnalyzer

        # 创建心理测评评估技能实例
        skill = PsychologicalAnalyzer()

        # 要分析的大五人格测试文件（正确路径）
        test_files = [
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214654.json',  # 基线
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214706.json',  # 轻度压力
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214717.json',  # 中度压力
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214728.json',  # 高度压力
            '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214812.json'   # 极度压力
        ]

        stress_conditions = ['基线', '轻度压力', '中度压力', '高度压力', '极度压力']

        print('🧠 大五人格压力测试心理评估分析')
        print('=' * 60)

        results = []

        for i, (file_path, condition) in enumerate(zip(test_files, stress_conditions)):
            print(f'\n{condition}条件分析:')
            print('-' * 30)

            if not os.path.exists(file_path):
                print(f'❌ 文件不存在: {file_path}')
                continue

            try:
                # 读取测试数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)

                # 使用心理测评技能分析
                analysis = skill.complete_evaluation(test_data)

                if analysis.get('success'):
                    traits = analysis['big_five_traits']
                    mbti = analysis['mbti_assessment']

                    print(f'✅ 大五人格分数:')
                    print(f'  开放性(O): {traits["openness"]}')
                    print(f'  尽责性(C): {traits["conscientiousness"]}')
                    print(f'  外向性(E): {traits["extraversion"]}')
                    print(f'  宜人性(A): {traits["agreeableness"]}')
                    print(f'  神经质(N): {traits["neuroticism"]}')

                    print(f'🎯 MBTI类型: {mbti["type"]} ({mbti["description"]})')
                    print(f'置信度: {mbti["confidence"]}')

                    results.append({
                        'condition': condition,
                        'big_five': traits,
                        'mbti': mbti,
                        'file_path': file_path
                    })
                else:
                    print(f'❌ 分析失败: {analysis.get("error", "未知错误")}')

            except Exception as e:
                print(f'❌ 处理失败: {e}')

        print(f'\n📊 压力条件对比分析')
        print('=' * 60)

        if len(results) >= 2:
            print(f"{'条件':<12} {'O':<6} {'C':<6} {'E':<6} {'A':<6} {'N':<6} {'MBTI':<8} {'置信度':<8}")
            print('-' * 70)

            for result in results:
                traits = result['big_five']
                mbti = result['mbti']
                print(f'{result["condition"]:<12} '
                      f'{traits["openness"]:<6.1f} '
                      f'{traits["conscientiousness"]:<6.1f} '
                      f'{traits["extraversion"]:<6.1f} '
                      f'{traits["agreeableness"]:<6.1f} '
                      f'{traits["neuroticism"]:<6.1f} '
                      f'{mbti["type"]:<8} '
                      f'{mbti["confidence"]:<8.1f}')

            # 分析压力对人格特质的影响趋势
            print(f'\n📈 压力影响趋势分析:')
            print('-' * 30)

            if len(results) >= 2:
                # 计算各维度从基线到极度压力的变化
                baseline = results[0]['big_five']
                extreme = results[-1]['big_five']

                changes = {}
                for trait in baseline:
                    change = extreme[trait] - baseline[trait]
                    changes[trait] = change
                    trait_names = {
                        'openness': '开放性',
                        'conscientiousness': '尽责性',
                        'extraversion': '外向性',
                        'agreeableness': '宜人性',
                        'neuroticism': '神经质'
                    }
                    trend = '↑' if change > 0.5 else '↓' if change < -0.5 else '→'
                    print(f'{trait_names[trait]}: {baseline[trait]:.1f} → {extreme[trait]:.1f} ({trend} {change:+.1f})')

            # MBTI类型变化分析
            print(f'\n🎭 MBTI类型变化:')
            print('-' * 20)
            for result in results:
                mbti = result['mbti']
                print(f'{result["condition"]}: {mbti["type"]} (置信度: {mbti["confidence"]:.1f})')

        else:
            print('❌ 可分析结果不足，无法进行对比')

        # 保存完整分析结果
        output_file = 'results/big_five_stress_psychological_analysis.json'
        if results:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'analysis_time': '2025-11-09T22:35:00',
                    'test_type': 'big_five_stress_analysis',
                    'conditions_analyzed': len(results),
                    'results': results
                }, f, ensure_ascii=False, indent=2)

            print(f'\n💾 完整分析结果已保存至: {output_file}')

    except ImportError as e:
        print(f'❌ 无法导入心理测评技能: {e}')
        print('请检查技能文件是否存在')
    except Exception as e:
        print(f'❌ 分析过程出错: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()