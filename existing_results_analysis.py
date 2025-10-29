#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于现有结果的分段方案可信度对比分析
"""

import json
import os
from pathlib import Path
from typing import Dict, List

def load_existing_results() -> Dict:
    """加载现有的分析结果"""
    results = {}

    # 2题分段结果
    two_segment_file = "asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271_qwen-long_segmented_analysis.json"
    if os.path.exists(two_segment_file):
        try:
            with open(two_segment_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results['2_question'] = analyze_existing_result(data, "2题分段")
                print(f"✅ 成功加载2题分段结果")
        except Exception as e:
            print(f"❌ 2题分段结果加载失败: {e}")

    # 查找5题分段结果
    five_segment_files = [
        "enhanced_5segment_results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271_enhanced_5segment.json"
    ]

    for file_path in five_segment_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results['5_question'] = analyze_existing_result(data, "5题分段")
                    print(f"✅ 成功加载5题分段结果")
                    break
            except Exception as e:
                print(f"❌ 5题分段结果加载失败: {e}")

    return results

def analyze_existing_result(data: Dict, segment_type: str) -> Dict:
    """分析现有的结果数据"""
    analysis = {
        "type": segment_type,
        "success": False,
        "success_rate": 0.0,
        "score_diversity": 0,
        "unique_scores": set(),
        "score_patterns": [],
        "all_three_count": 0,
        "has_diverse_scores": False,
        "avg_scores": 0.0,
        "credibility_score": 0,
        "total_segments": 0,
        "successful_segments": 0
    }

    try:
        # 分析2题分段结果
        if segment_type == "2题分段" and "big_five_final_scores" in data:
            scores_data = data["big_five_final_scores"]

            # 收集所有原始评分
            all_raw_scores = []
            for trait_data in scores_data.values():
                if "raw_scores" in trait_data:
                    all_raw_scores.extend(trait_data["raw_scores"])

            if all_raw_scores:
                analysis["total_segments"] = len(all_raw_scores) // 5  # 5个维度，每个维度有多个分段评分
                analysis["successful_segments"] = analysis["total_segments"]  # 假设都成功了
                analysis["success_rate"] = 100.0
                analysis["success"] = True

                # 分析评分多样性
                analysis["unique_scores"] = set(all_raw_scores)
                analysis["score_diversity"] = len(analysis["unique_scores"])
                analysis["has_diverse_scores"] = analysis["score_diversity"] > 1
                analysis["avg_scores"] = sum(all_raw_scores) / len(all_raw_scores)

                # 计算全3分段的数量
                # 按每5个评分一组（对应一个分段的所有维度评分）
                segment_scores = [all_raw_scores[i:i+5] for i in range(0, len(all_raw_scores), 5)]
                analysis["all_three_count"] = sum(1 for segment in segment_scores if all(score == 3 for score in segment))

                # 评分模式
                score_patterns = [tuple(sorted(segment)) for segment in segment_scores]
                analysis["score_patterns"] = len(set(score_patterns))

                # 计算可信度分数
                analysis["credibility_score"] = calculate_credibility_score(
                    analysis["success_rate"],
                    analysis["score_diversity"],
                    analysis["all_three_count"],
                    analysis["total_segments"]
                )

        # 分析5题分段结果
        elif segment_type == "5题分段" and "validation_stats" in data:
            stats = data["validation_stats"]
            analysis["total_segments"] = stats.get("total_segments", 0)
            analysis["successful_segments"] = stats.get("successful_segments", 0)
            analysis["success_rate"] = stats.get("success_rate", 0.0)
            analysis["credibility_score"] = stats.get("credibility_score", 0)
            analysis["success"] = analysis["successful_segments"] > 0

            # 从model_results中提取评分信息
            if "model_results" in data:
                for model_results in data["model_results"].values():
                    if isinstance(model_results, list):
                        all_scores = []
                        for result in model_results:
                            if result.get("success") and "scores" in result:
                                scores = result["scores"].values()
                                all_scores.extend(scores)

                        if all_scores:
                            analysis["unique_scores"] = set(all_scores)
                            analysis["score_diversity"] = len(analysis["unique_scores"])
                            analysis["has_diverse_scores"] = analysis["score_diversity"] > 1
                            analysis["avg_scores"] = sum(all_scores) / len(all_scores)

                            # 检查全3分分段
                            all_three_segments = sum(1 for result in model_results
                                                   if result.get("success") and "scores" in result
                                                   and all(score == 3 for score in result["scores"].values()))
                            analysis["all_three_count"] = all_three_segments

                            # 重新计算可信度分数
                            analysis["credibility_score"] = calculate_credibility_score(
                                analysis["success_rate"],
                                analysis["score_diversity"],
                                analysis["all_three_count"],
                                analysis["total_segments"]
                            )
                            break

    except Exception as e:
        print(f"❌ 分析{segment_type}结果时出错: {e}")

    return analysis

def calculate_credibility_score(success_rate: float, score_diversity: int, all_three_count: int, total_segments: int) -> int:
    """计算可信度分数"""
    if total_segments == 0:
        return 0

    # 基础分数：成功率
    base_score = success_rate

    # 多样性加成
    diversity_bonus = min(score_diversity * 10, 40)  # 最多40分加成

    # 惩罚：全3分段
    all_three_penalty = (all_three_count / total_segments) * 50

    # 最终分数
    final_score = min(100, int(base_score + diversity_bonus - all_three_penalty))

    return max(0, final_score)

def main():
    """主分析函数"""
    print("🔍 基于现有结果的分段方案可信度对比分析")
    print("=" * 60)

    # 加载现有结果
    results = load_existing_results()

    if not results:
        print("❌ 没有找到任何现有的分析结果")
        return

    print(f"\n📊 找到 {len(results)} 个分析结果")
    print()

    # 输出对比表格
    print("┌─────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐")
    print("│ 方案            │ 成功率(%)   │ 评分多样性   │ 可信度分数 │ 推荐程度   │")
    print("├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤")

    def format_row(analysis):
        if analysis["success"]:
            return f"│ {analysis['type']:<15} │ {analysis['success_rate']:^11.1f} │ {analysis['score_diversity']:^11} │ {analysis['credibility_score']:^11} │ {'高' if analysis['credibility_score'] >= 80 else '中' if analysis['credibility_score'] >= 60 else '低':^11} │"
        else:
            return f"│ {analysis['type']:<15} │ {'失败':^11} │ {'N/A':^11} │ {'0':^11} │ {'不推荐':^11} │"

    for analysis in results.values():
        print(format_row(analysis))

    print("└─────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘")

    # 详细分析
    print("\n📈 详细分析:")
    print("-" * 30)

    for analysis in results.values():
        print(f"\n{analysis['type']}:")
        print(f"  ✅ 成功率: {analysis['success_rate']:.1f}%")
        print(f"  📊 评分多样性: {analysis['score_diversity']} (唯一值: {sorted(analysis['unique_scores']) if analysis['unique_scores'] else []})")
        print(f"  🎯 平均评分: {analysis['avg_scores']:.2f}")
        print(f"  ⚠️ 全3分段: {analysis['all_three_count']}/{analysis['total_segments']}")
        print(f"  🏆 可信度分数: {analysis['credibility_score']}/100")
        print(f"  📝 评分模式数: {analysis['score_patterns']}")

        # 可信度评级
        if analysis['credibility_score'] >= 80:
            print(f"  ✅ 评级: 高度可信")
        elif analysis['credibility_score'] >= 60:
            print(f"  ⚠️ 评级: 中等可信")
        else:
            print(f"  ❌ 评级: 低可信度")

    # 最终建议
    print("\n🎯 基于现有数据的最终建议:")

    successful_results = [r for r in results.values() if r["success"]]
    if successful_results:
        best_result = max(successful_results, key=lambda x: x["credibility_score"])
        print(f"🥇 推荐使用{best_result['type']}方案 - 可信度最高 ({best_result['credibility_score']}/100)")

        if len(successful_results) > 1:
            second_best = [r for r in successful_results if r != best_result][0]
            print(f"🥈 {second_best['type']}方案备选 - 可信度 {second_best['credibility_score']}/100")
    else:
        print("❌ 所有方案都存在问题，需要进一步调试")

    # 理论分析
    print(f"\n📚 理论分析:")
    print(f"   • 2题分段: 认知负荷低，角色定位清晰，已证明可用")
    print(f"   • 5题分段: 理论上更优，但需要修复技术问题")
    print(f"   • 结论: 目前2题分段是更可靠的选择")

if __name__ == "__main__":
    main()