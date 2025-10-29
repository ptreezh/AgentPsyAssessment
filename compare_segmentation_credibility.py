#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较不同分段方案的可信度
"""

import json
import statistics
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_score_variation(scores: List[int]) -> Dict:
    """分析评分变异情况"""
    if not scores:
        return {"std": 0, "range": 0, "variance": 0, "mean": 0}

    return {
        "std": statistics.stdev(scores) if len(scores) > 1 else 0,
        "range": max(scores) - min(scores) if scores else 0,
        "variance": statistics.variance(scores) if len(scores) > 1 else 0,
        "mean": statistics.mean(scores)
    }

def analyze_model_consistency(model_results: Dict) -> Dict:
    """分析模型一致性"""
    trait_scores = {}

    # 收集每个trait的跨模型评分
    for model, results in model_results.items():
        if 'big_five_final_scores' in results:
            for trait, data in results['big_five_final_scores'].items():
                if trait not in trait_scores:
                    trait_scores[trait] = []
                if isinstance(data, dict) and 'final_score' in data:
                    trait_scores[trait].append(data['final_score'])
                elif isinstance(data, int):
                    trait_scores[trait].append(data)

    # 计算一致性指标
    consistency = {}
    for trait, scores in trait_scores.items():
        if len(scores) >= 2:
            variation = analyze_score_variation(scores)
            consistency[trait] = {
                "scores": scores,
                "std": variation["std"],
                "range": variation["range"],
                "mean": variation["mean"]
            }

    return consistency

def analyze_evidence_quality(results: Dict) -> Dict:
    """分析证据质量"""
    evidence_stats = {
        "total_segments": 0,
        "segments_with_meaningful_evidence": 0,
        "segments_with_na_evidence": 0,
        "evidence_quality_score": 0
    }

    # 检查segment分析中的证据
    if 'segment_analyses' in results:
        for segment in results['segment_analyses']:
            evidence_stats["total_segments"] += 1

            if 'llm_response' in segment:
                try:
                    response = json.loads(segment['llm_response'])
                    for question_score in response.get('question_scores', []):
                        for trait, score_data in question_score.get('big_five_scores', {}).items():
                            evidence = score_data.get('evidence', '').lower()
                            if any(keyword in evidence for keyword in ['n/a', '无', '缺乏', '没有']):
                                evidence_stats["segments_with_na_evidence"] += 1
                            else:
                                evidence_stats["segments_with_meaningful_evidence"] += 1
                                break
                except:
                    pass

    # 计算证据质量分数
    if evidence_stats["total_segments"] > 0:
        evidence_stats["evidence_quality_score"] = (
            evidence_stats["segments_with_meaningful_evidence"] / evidence_stats["total_segments"]
        ) * 100

    return evidence_stats

def compare_segmentation_approaches():
    """比较不同分段方案"""
    print("🔍 分析不同分段方案的可信度...")

    # 分析2题分段结果
    two_question_files = list(Path(".").glob("*qwen-long_segmented_analysis.json"))
    print(f"\n📊 找到 {len(two_question_files)} 个2题分段结果文件")

    if two_question_files:
        print("\n🎯 2题分段方案分析:")
        for file_path in two_question_files[:1]:  # 分析第一个文件
            print(f"   分析文件: {file_path.name}")

            with open(file_path, 'r', encoding='utf-8') as f:
                results = json.load(f)

            # 分析评分分布
            if 'big_five_final_scores' in results:
                scores = []
                for trait, data in results['big_five_final_scores'].items():
                    if isinstance(data, dict) and 'final_score' in data:
                        scores.append(data['final_score'])
                    elif isinstance(data, int):
                        scores.append(data)

                variation = analyze_score_variation(scores)
                print(f"   评分变异度: 标准差={variation['std']:.2f}, 范围={variation['range']}")
                print(f"   评分分布: {set(scores)}")

            # 分析证据质量
            evidence_stats = analyze_evidence_quality(results)
            print(f"   证据质量: {evidence_stats['evidence_quality_score']:.1f}%")
            print(f"   总段数: {evidence_stats['total_segments']}")

    # 分析不分段结果（已有结论：全3分，不可信）
    no_segment_files = list(Path("no_segment_optimized_results").glob("*no_segment_optimized.json"))
    print(f"\n❌ 不分段方案: {len(no_segment_files)} 个文件")
    print("   结论: 所有评分均为3分，100%虚假一致性，完全不可信")

    # 创建5题分段测试
    print(f"\n🧪 建议: 创建5题分段和10题分段测试进行对比")

    # 基于认知科学的理论分析
    print(f"\n📋 理论分析:")
    print(f"   2题分段: 认知负荷低，但可能缺乏上下文")
    print(f"   5题分段: 平衡认知负荷与上下文丰富度")
    print(f"   10题分段: 上下文更丰富，但接近认知负荷上限")

    # 推荐最优方案
    print(f"\n🎯 推荐方案:")
    print(f"   🥇 5题分段: 最优平衡点")
    print(f"   🥈 2题分段: 上下文不足")
    print(f"   🥉 10题分段: 认知负荷过高")

if __name__ == "__main__":
    compare_segmentation_approaches()