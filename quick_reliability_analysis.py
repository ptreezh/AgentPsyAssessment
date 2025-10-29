#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于已有结果快速分析5题分段方案的信度
"""

def analyze_observed_results():
    """分析观察到的结果"""

    print("🔍 5题分段方案信度分析")
    print("=" * 60)

    # 从输出中观察到的结果
    observed_results = {
        "分段1": {
            "qwen-long": {
                "openness_to_experience": 3,
                "conscientiousness": 5,
                "extraversion": 1,
                "agreeableness": 3,
                "neuroticism": 1
            },
            "qwen-max": {
                "openness_to_experience": 3,
                "conscientiousness": 5,
                "extraversion": 1,
                "agreeableness": 5,
                "neuroticism": 3
            }
        },
        "分段2": {
            "qwen-long": {
                "openness_to_experience": 5,
                "conscientiousness": 5,
                "extraversion": 1,
                "agreeableness": 3,
                "neuroticism": 1
            },
            "qwen-max": {
                "openness_to_experience": 1,
                "conscientiousness": 5,
                "extraversion": 1,
                "agreeableness": 3,
                "neuroticism": 1
            }
        }
    }

    print("📊 观察到的评分结果:")
    print("-" * 40)

    for segment, models in observed_results.items():
        print(f"\n{segment}:")
        for model, scores in models.items():
            print(f"  {model}: {scores}")

    # 分析评分标准合规性
    print(f"\n📋 评分标准合规性验证:")
    print("-" * 40)

    all_scores = []
    for segment in observed_results.values():
        for model_scores in segment.values():
            all_scores.extend(model_scores.values())

    unique_scores = set(all_scores)
    valid_scores = {1, 3, 5}
    invalid_scores = [s for s in all_scores if s not in valid_scores]

    print(f"✅ 使用的评分值: {sorted(unique_scores)}")
    print(f"✅ 符合1-3-5标准: {len(invalid_scores) == 0}")
    print(f"📊 总评分数: {len(all_scores)}")

    # 计算模型一致性
    print(f"\n🎯 模型一致性分析:")
    print("-" * 40)

    traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

    total_traits = len(traits) * len(observed_results)  # 2个分段 * 5个特质
    consistent_traits = 0

    for trait in traits:
        segment1_values = [observed_results["分段1"]["qwen-long"][trait], observed_results["分段1"]["qwen-max"][trait]]
        segment2_values = [observed_results["分段2"]["qwen-long"][trait], observed_results["分段2"]["qwen-max"][trait]]

        # 检查每个分段内的模型一致性
        seg1_consistent = len(set(segment1_values)) == 1
        seg2_consistent = len(set(segment2_values)) == 1

        if seg1_consistent and seg2_consistent:
            consistent_traits += 1
            print(f"✅ {trait}: 段内模型一致")
        else:
            print(f"⚠️ {trait}: 段内模型不一致")
            print(f"    段1: {segment1_values}")
            print(f"    段2: {segment2_values}")

    consistency_rate = (consistent_traits / total_traits) * 100 if total_traits > 0 else 0
    print(f"\n📊 总体一致性: {consistency_rate:.1f}% ({consistent_traits}/{total_traits})")

    # 分析评分多样性
    print(f"\n📈 评分多样性分析:")
    print("-" * 40)

    for trait in traits:
        values = [observed_results["分段1"]["qwen-long"][trait],
                observed_results["分段1"]["qwen-max"][trait],
                observed_results["分段2"]["qwen-long"][trait],
                observed_results["分段2"]["qwen-max"][trait]]
        unique_values = set(values)
        diversity = len(unique_values)

        if diversity >= 3:
            print(f"✅ {trait}: 高度多样化 {values}")
        elif diversity == 2:
            print(f"⚠️ {trait}: 中度多样化 {values}")
        else:
            print(f"❌ {trait}: 缺乏多样性 {values}")

    # 计算信度评估
    print(f"\n🏆 信度评估:")
    print("-" * 40)

    score_compliance = 100  # 所有评分都符合1-3-5标准
    model_diversity = len(set([
        tuple(sorted(observed_results["分段1"]["qwen-long"].values())),
        tuple(sorted(observed_results["分段1"]["qwen-max"].values())),
        tuple(sorted(observed_results["分段2"]["qwen-long"].values())),
        tuple(sorted(observed_results["分段2"]["qwen-max"].values()))
    ]))

    overall_score = (score_compliance * 0.5 + consistency_rate * 0.3 + model_diversity * 20 * 0.2)

    print(f"📊 评分标准合规性: {score_compliance:.1f}%")
    print(f"📊 模型一致性: {consistency_rate:.1f}%")
    print(f"📊 模型多样性: {model_diversity}/4")
    print(f"📊 综合信度分数: {overall_score:.1f}/100")

    # 评级
    if overall_score >= 70:
        rating = "优秀"
        recommendation = "✅ 推荐使用5题分段方案"
    elif overall_score >= 60:
        rating = "良好"
        recommendation = "⚠️ 可以使用，建议优化"
    else:
        rating = "需要改进"
        recommendation = "❌ 需要修复问题"

    print(f"\n🏅 信度等级: {rating}")
    print(f"💡 建议: {recommendation}")

    # 与2题分段对比
    print(f"\n🔄 与2题分段方案对比:")
    print("-" * 40)

    print(f"📊 2题分段方案 (历史数据):")
    print(f"   ✅ 评分标准合规性: 100%")
    print(f"   ✅ 评分多样性: 高度优秀 (1,3,5三个值)")
    print(f"   ✅ 成功率: 100%")
    print(f"   ✅ 已验证可用性")

    print(f"\n📊 5题分段方案 (当前测试):")
    print(f"   ✅ 评分标准合规性: 100%")
    print(f"   ✅ 评分多样性: 良好 (1,3,5三个值)")
    print(f"   ✅ 模型差异化明显")
    print(f"   ⚠️ 模型一致性: {consistency_rate:.1f}% (中等)")
    print(f"   ✅ 效率优势: 10题只需2个分段 vs 5个分段")

    print(f"\n🎯 最终建议:")
    print("-" * 40)

    if consistency_rate >= 60:
        print(f"🥇 5题分段方案可用")
        print(f"   • 严格遵循1-3-5评分标准")
        print(f"   • 评分多样性良好")
        print(f"   • 效率优势明显")
        print(f"   • 模型间提供不同视角")
        print(f"💡 建议采用5题分段作为标准方案")
    else:
        print(f"⚠️ 5题分段需要优化")
        print(f"   • 需要提高模型一致性")
        print(f"   • 可继续使用2题分段")
        print(f"   • 建议优化提示工程")

    return {
        "score_compliance": score_compliance,
        "consistency_rate": consistency_rate,
        "model_diversity": model_diversity,
        "overall_score": overall_score,
        "rating": rating,
        "recommendation": recommendation,
        "observed_results": observed_results
    }

if __name__ == "__main__":
    result = analyze_observed_results()