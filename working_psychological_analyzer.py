#!/usr/bin/env python3
"""
工作版心理测评分析器
基于成功的单个问题评估生成大五人格压力测试完整报告
"""

import sys
import os
import json
import statistics

# 添加技能路径
sys.path.append('.claude/skills/psychological-analyzer')

def calculate_final_scores(dimension_scores: dict) -> dict:
    """计算各维度最终分数"""
    final_scores = {}

    for dimension in ["O", "C", "E", "A", "N"]:
        scores = dimension_scores.get(dimension, [])
        if scores:
            avg_score = statistics.mean(scores)
            final_scores[dimension] = round(avg_score, 2)
        else:
            final_scores[dimension] = 3.0  # 默认中等分

    return final_scores

def infer_mbti_type(big_five_scores: dict) -> dict:
    """基于大五人格分数推断MBTI类型"""

    # E/I 判断 (基于外向性)
    e_score = big_five_scores.get('E', 3.0)
    ei_type = 'E' if e_score > 3.5 else 'I'

    # S/N 判断 (基于开放性，反向)
    o_score = big_five_scores.get('O', 3.0)
    sn_type = 'S' if o_score < 3.5 else 'N'

    # T/F 判断 (基于宜人性，反向)
    a_score = big_five_scores.get('A', 3.0)
    tf_type = 'T' if a_score < 3.5 else 'F'

    # J/P 判断 (基于尽责性)
    c_score = big_five_scores.get('C', 3.0)
    jp_type = 'J' if c_score > 3.5 else 'P'

    mbti_type = ei_type + sn_type + tf_type + jp_type

    # MBTI类型描述
    mbti_descriptions = {
        'ISTJ': '物流师 - 务实、可靠、有条理',
        'ISFJ': '守护者 - 温暖、利他、尽责',
        'INFJ': '提倡者 - 理想主义、洞察力、奉献',
        'INTJ': '建筑师 - 战略性、独立思考',
        'ISTP': '鉴赏家 - 灵活、冷静、实用',
        'ISFP': '探险家 - 艺术性、敏感、自由',
        'INFP': '调停者 - 价值驱动、和谐',
        'INTP': '思想家 - 逻辑性、好奇心强',
        'ESTP': '企业家 - 精力充沛、冒险性',
        'ESFP': '娱乐家 - 热情、社交性强',
        'ESTJ': '总经理 - 高效、传统、可靠',
        'ESFJ': '执政官 - 和谐、利他、社交',
        'ENTP': '辩论家 - 创新性、适应性、聪明',
        'ENTJ': '指挥官 - 领导力、战略性、果断',
        'ENFP': '竞选者 - 热情、创造力、社交性',
        'ENFJ': '主人公 - 魅力、利他主义、领导力'
    }

    # 计算置信度
    confidence_scores = {
        'EI': abs(e_score - 3.5) * 20,
        'SN': abs(o_score - 3.5) * 20,
        'TF': abs(a_score - 3.5) * 20,
        'JP': abs(c_score - 3.5) * 20
    }

    avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)

    return {
        'type': mbti_type,
        'description': mbti_descriptions.get(mbti_type, '未知类型'),
        'confidence': min(100, max(0, avg_confidence)),
        'dimension_scores': {
            'E/I': f'{e_score:.1f} ({"E" if e_score > 3.5 else "I"})',
            'S/N': f'{o_score:.1f} ({"S" if o_score < 3.5 else "N"})',
            'T/F': f'{a_score:.1f} ({"T" if a_score < 3.5 else "F"})',
            'J/P': f'{c_score:.1f} ({"J" if c_score > 3.5 else "P"})'
        }
    }

def analyze_with_working_psychological_skill(test_data: dict) -> dict:
    """使用工作版心理测评技能分析测试数据"""
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

        # 启动评估会话
        total_questions = len(answers)
        session_result = skill.start_evaluation_session(total_questions)

        print(f"✅ 成功启动评估会话: {session_result['session_id']}")

        # 逐个评估每个问题
        dimension_scores = {"O": [], "C": [], "E": [], "A": [], "N": []}
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

                if 'error' not in result:
                    all_results.append(result)

                    # 记录维度分数
                    scores = result.get('scores', {})
                    for dim, score in scores.items():
                        if 1 <= score <= 5:
                            dimension_scores[dim].append(score)

                    print(f"  ✅ 评估成功: {scores}")
                else:
                    print(f"  ❌ 评估失败: {result.get('error', '未知错误')}")

            except Exception as e:
                print(f"  ❌ 评估异常: {e}")

        # 计算最终结果
        final_scores = calculate_final_scores(dimension_scores)
        mbti_result = infer_mbti_type(final_scores)

        # 构建成功报告
        report = {
            'session_info': {
                'session_id': session_result['session_id'],
                'evaluation_date': session_result['session_timestamp'],
                'total_questions': total_questions,
                'completed_questions': len(all_results)
            },
            'big_five_traits': {
                'openness': final_scores['O'],
                'conscientiousness': final_scores['C'],
                'extraversion': final_scores['E'],
                'agreeableness': final_scores['A'],
                'neuroticism': final_scores['N']
            },
            'mbti_assessment': mbti_result,
            'question_details': all_results,
            'stress_parameters': {
                'emotional_stress': session_info.get('emotional_stress', 0),
                'cognitive_trap': session_info.get('cognitive_trap', ''),
                'context_tokens': session_info.get('context_tokens', 0),
                'temperature': session_info.get('temperature', 0.6),
                'role': session_info.get('role', 'default')
            },
            'success': True
        }

        return report

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

    print('🧠 使用工作版心理测评技能分析大五人格压力测试')
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

            # 使用工作版心理测评技能分析
            analysis = analyze_with_working_psychological_skill(test_data)

            if analysis.get('success'):
                print(f'✅ 分析成功!')

                # 显示大五人格分数
                big_five = analysis.get('big_five_traits', {})
                if big_five:
                    print(f'🎯 大五人格分数:')
                    print(f'  开放性(O): {big_five.get("openness", 0):.2f}')
                    print(f'  尽责性(C): {big_five.get("conscientiousness", 0):.2f}')
                    print(f'  外向性(E): {big_five.get("extraversion", 0):.2f}')
                    print(f'  宜人性(A): {big_five.get("agreeableness", 0):.2f}')
                    print(f'  神经质(N): {big_five.get("neuroticism", 0):.2f}')

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
        print(f"{'条件':<12} {'O':<6} {'C':<6} {'E':<6} {'A':<6} {'N':<6} {'MBTI':<8} {'置信度':<8}")
        print('-' * 70)

        for result in results:
            analysis = result['analysis']
            big_five = analysis.get('big_five_traits', {})
            o = big_five.get('openness', 0)
            c = big_five.get('conscientiousness', 0)
            e = big_five.get('extraversion', 0)
            a = big_five.get('agreeableness', 0)
            n = big_five.get('neuroticism', 0)

            mbti = analysis.get('mbti_assessment', {})
            mbti_type = mbti.get('type', 'Unknown')

            print(f'{result["condition"]:<12} '
                  f'{o:<6.2f} {c:<6.2f} {e:<6.2f} {a:<6.2f} {n:<6.2f} {mbti_type:<8} '
                  f'{mbti.get("confidence", 0):.1f}')

        # 趋势分析
        print(f'\n📈 压力影响趋势分析:')
        print('-' * 30)

        baseline_big_five = results[0]['analysis'].get('big_five_traits', {})
        for i, result in enumerate(results[1:], 1):
            current_big_five = result['analysis'].get('big_five_traits', {})
            changes = {}

            for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
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
                'openness': '开放性',
                'conscientiousness': '尽责性',
                'extraversion': '外向性',
                'agreeableness': '宜人性',
                'neuroticism': '神经质'
            }

            print(f'  详细变化:')
            for trait, change in changes.items():
                if abs(change) > 0.1:
                    trend = '↑' if change > 0 else '↓'
                    print(f'    {trait_names[trait]}: {baseline_val:.2f} → {current_val:.2f} ({trend} {change:+.2f})')

        # MBTI类型变化
        print(f'\n🎭 MBTI类型变化:')
        print('-' * 20)
        for result in results:
            mbti = result['analysis'].get('mbti_assessment', {})
            print(f'{result["condition"]}: {mbti.get("type", "Unknown")} (置信度: {mbti.get("confidence", 0):.1f}%)')

    # 保存结果
    if results:
        output_file = 'results/big_five_working_psychological_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_time': '2025-11-09T22:55:00',
                'test_type': 'big_five_stress_working_psychological',
                'conditions_analyzed': len(results),
                'results': results
            }, f, ensure_ascii=False, indent=2)

        print(f'\n💾 工作版分析结果已保存至: {output_file}')
        print(f'\n✅ 成功使用心理测评技能完成大五人格压力测试分析！')

if __name__ == "__main__":
    main()