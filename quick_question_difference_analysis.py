#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于已获得的50题5题分段评分进行逐题差异分析
"""

import json
from datetime import datetime
from typing import Dict, List

def analyze_question_level_differences():
    """分析逐题差异"""

    print("📊 50题5题分段逐题评分差异分析")
    print("=" * 50)

    # 50题的5题分段评分数据（从上面的输出提取）
    question_5segment_scores = {
        1: {'openness_to_experience': 5, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 1},
        2: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        3: {'openness_to_experience': 5, 'conscientiousness': 5, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 1},
        4: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 3, 'agreeableness': 5, 'neuroticism': 1},
        5: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        6: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        7: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 3},
        8: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        9: {'openness_to_experience': 5, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 5, 'neuroticism': 1},
        10: {'openness_to_experience': 5, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 1},
        11: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        12: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 5, 'neuroticism': 1},
        13: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        14: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        15: {'openness_to_experience': 5, 'conscientiousness': 5, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 1},
        16: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        17: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        18: {'openness_to_experience': 5, 'conscientiousness': 5, 'extraversion': 3, 'agreeableness': 3, 'neuroticism': 1},
        19: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        20: {'openness_to_experience': 1, 'conscientiousness': 3, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        21: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        22: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        23: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        24: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        25: {'openness_to_experience': 1, 'conscientiousness': 3, 'extraversion': 3, 'agreeableness': 1, 'neuroticism': 3},
        26: {'openness_to_experience': 1, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        27: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        28: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 5, 'neuroticism': 1},
        29: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        30: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        31: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        32: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        33: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        34: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        35: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        36: {'openness_to_experience': 1, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 3},
        37: {'openness_to_experience': 3, 'conscientiousness': 3, 'extraversion': 1, 'agreeableness': 5, 'neuroticism': 1},
        38: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        39: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 3, 'agreeableness': 5, 'neuroticism': 1},
        40: {'openness_to_experience': 1, 'conscientiousness': 3, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        41: {'openness_to_experience': 5, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        42: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        43: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        44: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        45: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        46: {'openness_to_experience': 5, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        47: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        48: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        49: {'openness_to_experience': 3, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1},
        50: {'openness_to_experience': 1, 'conscientiousness': 5, 'extraversion': 1, 'agreeableness': 3, 'neuroticism': 1}
    }

    # 从2题分段分析文件中提取的最终评分
    final_2segment_scores = {
        'openness_to_experience': 3,
        'conscientiousness': 5,
        'extraversion': 1,
        'agreeableness': 3,
        'neuroticism': 1
    }

    # 分析逐题与最终2题分段评分的差异
    print(f"📋 逐题与2题分段最终评分的差异分析:")
    print("-" * 50)

    traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

    total_questions = len(question_5segment_scores)
    trait_differences = {trait: [] for trait in traits}
    question_differences = []

    for q_num, scores in question_5segment_scores.items():
        question_diff = {
            'question': q_num,
            'trait_differences': {},
            'total_difference': 0,
            'consistent_traits': 0
        }

        total_diff = 0
        consistent_count = 0

        for trait in traits:
            diff = abs(scores[trait] - final_2segment_scores[trait])
            trait_differences[trait].append(diff)

            question_diff['trait_differences'][trait] = {
                'question_score': scores[trait],
                'final_2segment_score': final_2segment_scores[trait],
                'difference': diff,
                'consistent': diff == 0
            }

            total_diff += diff
            if diff == 0:
                consistent_count += 1

        question_diff['total_difference'] = total_diff
        question_diff['consistent_traits'] = consistent_count
        question_diff['inconsistent_traits'] = 5 - consistent_count

        question_differences.append(question_diff)

    # 统计分析
    print(f"📊 特质层面差异统计:")
    for trait, differences in trait_differences.items():
        avg_diff = sum(differences) / len(differences)
        max_diff = max(differences)
        min_diff = min(differences)
        consistent_count = differences.count(0)

        print(f"  {trait}:")
        print(f"    平均差异: {avg_diff:.2f}")
        print(f"    最大差异: {max_diff}")
        print(f"    最小差异: {min_diff}")
        print(f"    完全一致题数: {consistent_count}/50 ({consistent_count*2}%)")
        print()

    # 问题层面统计
    print(f"📈 问题层面差异统计:")

    # 按差异程度分类
    perfect_consistent = [q for q in question_differences if q['consistent_traits'] == 5]
    high_consistent = [q for q in question_differences if q['consistent_traits'] >= 4]
    medium_consistent = [q for q in question_differences if q['consistent_traits'] >= 3]
    low_consistent = [q for q in question_differences if q['consistent_traits'] < 3]

    print(f"  完全一致 (5/5特质): {len(perfect_consistent)}题 ({len(perfect_consistent)*2}%)")
    print(f"  高度一致 (≥4特质): {len(high_consistent)}题 ({len(high_consistent)*2}%)")
    print(f"  中度一致 (≥3特质): {len(medium_consistent)}题 ({len(medium_consistent)*2}%)")
    print(f"  低度一致 (<3特质): {len(low_consistent)}题 ({len(low_consistent)*2}%)")

    avg_consistent_traits = sum(q['consistent_traits'] for q in question_differences) / total_questions
    print(f"  平均每题一致特质数: {avg_consistent_traits:.2f}/5")

    # 找出最一致和最不一致的问题
    most_consistent = sorted(question_differences, key=lambda x: x['consistent_traits'], reverse=True)[:10]
    least_consistent = sorted(question_differences, key=lambda x: x['consistent_traits'])[:10]

    print(f"\n🏆 最一致的10题:")
    for i, q in enumerate(most_consistent, 1):
        print(f"  {i}. 题{q['question']}: {q['consistent_traits']}/5特质一致 (总差异: {q['total_difference']})")

    print(f"\n⚠️ 最不一致的10题:")
    for i, q in enumerate(least_consistent, 1):
        print(f"  {i}. 题{q['question']}: {q['consistent_traits']}/5特质一致 (总差异: {q['total_difference']})")
        if q['total_difference'] > 0:
            inconsistent_traits = [trait for trait, diff in q['trait_differences'].items() if not diff['consistent']]
            print(f"      不一致特质: {', '.join(inconsistent_traits)}")

    # 计算总体一致性评估
    perfect_rate = len(perfect_consistent) / total_questions
    high_rate = len(high_consistent) / total_questions

    if perfect_rate >= 0.8:
        reliability = "优秀"
        recommendation = "✅ 逐题与最终评分高度一致，5题分段方案可信"
    elif high_rate >= 0.8:
        reliability = "良好"
        recommendation = "✅ 大部分问题与最终评分一致，5题分段方案可用"
    elif avg_consistent_traits >= 3:
        reliability = "中等"
        recommendation = "⚠️ 存在一定差异，需要关注个别问题"
    else:
        reliability = "需要改进"
        recommendation = "❌ 差异较大，需要重新评估"

    print(f"\n🎯 总体评估:")
    print(f"  可靠性等级: {reliability}")
    print(f"  完全一致率: {perfect_rate*100:.1f}%")
    print(f"  高度一致率: {high_rate*100:.1f}%")
    print(f"  建议: {recommendation}")

    # 分析差异模式
    print(f"\n🔍 差异模式分析:")
    all_differences = [q['total_difference'] for q in question_differences]
    max_total_diff = max(all_differences)

    # 找出有差异的问题
    questions_with_differences = [q for q in question_differences if q['total_difference'] > 0]

    print(f"  有差异的题数: {len(questions_with_differences)}/50 ({len(questions_with_differences)*2}%)")
    print(f"  最大单题差异: {max_total_diff}")

    if len(questions_with_differences) > 0:
        print(f"  差异主要来源:")
        trait_diff_counts = {trait: 0 for trait in traits}
        for q in questions_with_differences:
            for trait, diff in q['trait_differences'].items():
                if not diff['consistent']:
                    trait_diff_counts[trait] += 1

        for trait, count in sorted(trait_diff_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"    {trait}: {count}题有差异")

    # 保存结果
    analysis_result = {
        "analysis_info": {
            "total_questions": total_questions,
            "analysis_date": datetime.now().isoformat(),
            "method": "5题分段逐题评分 vs 2题分段最终评分对比"
        },
        "final_2segment_scores": final_2segment_scores,
        "trait_statistics": {
            trait: {
                "average_difference": sum(trait_differences[trait]) / len(trait_differences[trait]),
                "max_difference": max(trait_differences[trait]),
                "consistent_questions": trait_differences[trait].count(0),
                "consistency_rate": (trait_differences[trait].count(0) / total_questions) * 100
            }
            for trait in traits
        },
        "question_statistics": {
            "perfect_consistent": len(perfect_consistent),
            "high_consistent": len(high_consistent),
            "medium_consistent": len(medium_consistent),
            "low_consistent": len(low_consistent),
            "average_consistent_traits": avg_consistent_traits,
            "questions_with_differences": len(questions_with_differences)
        },
        "overall_assessment": {
            "reliability": reliability,
            "recommendation": recommendation,
            "perfect_consistency_rate": perfect_rate * 100,
            "high_consistency_rate": high_rate * 100
        },
        "question_differences": question_differences,
        "most_consistent_questions": most_consistent,
        "least_consistent_questions": least_consistent
    }

    with open("question_by_question_difference_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 分析结果已保存: question_by_question_difference_analysis.json")

    return analysis_result

if __name__ == "__main__":
    result = analyze_question_level_differences()