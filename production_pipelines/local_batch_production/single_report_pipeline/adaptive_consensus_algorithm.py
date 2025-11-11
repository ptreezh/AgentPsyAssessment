#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能适应性共识算法
基于用户需求的动态评估器共识算法
当出现分歧时自动增加评估器直到达成可靠共识
"""

import statistics
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import random


class AdaptiveConsensusAlgorithm:
    """
    智能适应性共识算法

    核心特性：
    1. 基础3个评估器，评分只能是1, 3, 5
    2. 自动检测分歧程度
    3. 动态增加评估器直到达成共识
    4. 智能偏差检测和排除
    5. 最多扩展到7个评估器
    """

    def __init__(self):
        # 算法参数
        self.initial_evaluators = 3
        self.max_evaluators = 7
        self.allowed_scores = [1, 3, 5]  # 只允许奇数评分
        self.consensus_threshold = 2.0    # 最大允许差异
        self.bias_detection_threshold = 1.5  # 偏差检测阈值

        # 评估器池（用于动态扩展）
        self.evaluator_pool = [
            'evaluator_a', 'evaluator_b', 'evaluator_c',
            'evaluator_d', 'evaluator_e', 'evaluator_f', 'evaluator_g'
        ]

    def adaptive_consensus(self, initial_scores: List[int],
                          get_additional_scores: callable) -> Dict[str, Any]:
        """
        自适应共识算法主入口

        Args:
            initial_scores: 初始3个评估器的评分 [1,3,5]
            get_additional_scores: 获取额外评估器评分的函数

        Returns:
            共识结果字典
        """
        if len(initial_scores) != 3:
            raise ValueError("初始评分必须恰好包含3个评估器的评分")

        # 验证评分合法性
        if not all(score in self.allowed_scores for score in initial_scores):
            raise ValueError("评分只能是1, 3, 5")

        return self._adaptive_consensus_process(initial_scores, get_additional_scores)

    def _adaptive_consensus_process(self, scores: List[int],
                                  get_additional_scores: callable,
                                  round_num: int = 1) -> Dict[str, Any]:
        """递归共识处理过程"""

        print(f"🔄 第{round_num}轮共识处理，当前评分: {scores}")

        # 计算当前评分的差异
        max_score, min_score = max(scores), min(scores)
        current_diff = max_score - min_score

        if current_diff == 0:
            # 情况1: 完全共识
            print(f"✅ 完全共识！所有评分都是 {max_score}")
            return self._create_result(scores, max_score, "perfect_consensus", round_num)

        elif current_diff <= 2:
            # 情况2: 轻微分歧 (差异≤2分)
            return self._handle_minor_disagreement(scores, round_num)

        elif current_diff == 4:
            # 情况3: 严重分歧 (差异=4分) - 简化处理
            return self._handle_major_disagreement_simple(scores, get_additional_scores, round_num)

        else:
            # 这种情况不应该发生（因为评分只能是1,3,5）
            raise ValueError(f"异常差异: {current_diff}")

    def _handle_minor_disagreement(self, scores: List[int], round_num: int) -> Dict[str, Any]:
        """处理轻微分歧（差异≤2分）"""

        score_counts = Counter(scores)

        if len(score_counts) == 2:
            # 有两个分数，一个轻微不同
            most_common = score_counts.most_common(1)[0][0]
            consensus_score = statistics.mean(scores)

            print(f"✅ 轻微分歧达成共识: {scores} -> 平均分 {consensus_score:.1f}")
            return self._create_result(scores, consensus_score, "minor_consensus", round_num)

        else:
            # 三个分数都不同，但差异在2分内（比如[1,3,3]或[3,5,5]）
            consensus_score = statistics.mean(scores)

            print(f"✅ 轻微分歧达成共识: {scores} -> 平均分 {consensus_score:.1f}")
            return self._create_result(scores, consensus_score, "minor_consensus", round_num)

    def _handle_major_disagreement_simple(self, scores: List[int], get_additional_scores: callable, round_num: int) -> Dict[str, Any]:
        """
        严重分歧处理（差异=4分）
        新规则：前面3个评估器只算作1个评分，然后继续下一轮共识
        """
        print(f"⚠️ 严重分歧处理: {scores} (差异=4分)")

        # 将前面3个评分合并为1个评分
        median_score = statistics.median(scores)

        # 判断是否有真正的中位数（即有重复值）
        score_counts = Counter(scores)
        has_median = any(count > 1 for count in score_counts.values())

        if has_median:
            # 有中位数（有重复值）
            consolidated_score = median_score
            print(f"🔄 3个评估器合并为1个评分: {scores} -> {consolidated_score} (取中位数)")
        else:
            # 没有中位数（三个分数都不同），取平均数
            consolidated_score = statistics.mean(scores)
            print(f"🔄 3个评估器合并为1个评分: {scores} -> {consolidated_score:.1f} (取平均数)")

        # 获取新的评估器评分（至少需要2个才能进行共识）
        new_scores = get_additional_scores(2)
        print(f"🔄 新增评估器评分: {new_scores}")

        # 将合并的评分与新评分一起进行下一轮共识
        all_scores = [int(consolidated_score)] + new_scores
        print(f"🔄 进入下一轮共识，当前评分: {all_scores}")

        # 递归处理下一轮共识
        return self._adaptive_consensus_process(all_scores, get_additional_scores, round_num + 1)

    def _handle_major_disagreement(self, scores: List[int],
                                 get_additional_scores: callable,
                                 round_num: int) -> Dict[str, Any]:
        """处理严重分歧（差异=4分）"""

        score_counts = Counter(scores)

        if len(score_counts) == 2:
            # 有两个相同分数，一个差异很大
            common_score, uncommon_score = score_counts.most_common(2)
            common_score = common_score[0]
            uncommon_score = uncommon_score[0]

            print(f"⚠️ 严重分歧检测到: {scores} (共识: {common_score}, 异常: {uncommon_score})")

            # 废弃差异大的分数，新增2个评估器
            new_scores = get_additional_scores(2)
            extended_scores = [common_score] + new_scores

            print(f"🔄 新增2个评估器评分: {new_scores}")

            # 检查新的一致性
            new_max, new_min = max(extended_scores), min(extended_scores)
            new_diff = new_max - new_min

            if new_diff <= 2:
                # 达成共识，取4个分数的平均
                consensus_score = statistics.mean(extended_scores)
                print(f"✅ 扩展后达成共识: {extended_scores} -> 平均分 {consensus_score:.1f}")
                return self._create_result(extended_scores, consensus_score, "extended_consensus", round_num)

            else:
                # 仍然分歧很大，进一步处理
                return self._handle_still_divided(extended_scores, uncommon_score,
                                                get_additional_scores, round_num)

        else:
            # 三个分数都不同（1,3,5），这确实差异4分
            # 这是最大分歧情况，需要特殊处理
            print(f"⚠️ 最大分歧检测到: {scores} (三个分数都不同)")
            # 直接进入扩展阶段
            new_scores = get_additional_scores(2)
            extended_scores = scores + new_scores

            print(f"🔄 新增2个评估器评分: {new_scores}")

            # 去掉偏差最大的两个分数
            bias_removed_scores = self._remove_max_bias(extended_scores, 2)
            consensus_score = statistics.mean(bias_removed_scores)

            print(f"✅ 最大分歧解决: {bias_removed_scores} -> 平均分 {consensus_score:.1f}")
            return self._create_result(bias_removed_scores, consensus_score, "max_divergence_consensus", round_num)

    def _handle_still_divided(self, current_scores: List[int],
                            discarded_score: int,
                            get_additional_scores: callable,
                            round_num: int) -> Dict[str, Any]:
        """处理扩展后仍然分歧的情况"""

        # 与原来废弃的分数比较
        all_scores = current_scores + [discarded_score]
        current_mean = statistics.mean(current_scores)

        if abs(discarded_score - current_mean) <= 2:
            # 废弃的分数其实并不太偏差，重新纳入考虑
            print(f"🔄 重新考虑废弃分数 {discarded_score}，当前5个评分: {all_scores}")

            # 去掉偏差最大的一个分数
            bias_removed_scores = self._remove_max_bias(all_scores, 1)
            consensus_score = statistics.mean(bias_removed_scores)

            print(f"✅ 去除最大偏差后达成共识: {bias_removed_scores} -> 平均分 {consensus_score:.1f}")
            return self._create_result(bias_removed_scores, consensus_score, "bias_removed_consensus", round_num)

        else:
            # 废弃的分数确实偏差很大，需要进一步扩展
            if len(current_scores) < 7:
                # 继续增加2个评估器
                new_scores = get_additional_scores(2)
                extended_scores = current_scores + new_scores

                print(f"🔄 进一步扩展，新增2个评估器: {new_scores}")
                print(f"📊 当前7个评分: {extended_scores}")

                # 去掉最大偏差的两个分数
                bias_removed_scores = self._remove_max_bias(extended_scores, 2)
                consensus_score = statistics.mean(bias_removed_scores)

                print(f"✅ 最终共识: {bias_removed_scores} -> 平均分 {consensus_score:.1f}")
                return self._create_result(bias_removed_scores, consensus_score, "final_consensus", round_num)
            else:
                # 已达到7个评估器的上限
                bias_removed_scores = self._remove_max_bias(current_scores, 1)
                consensus_score = statistics.mean(bias_removed_scores)

                print(f"⚠️ 达到评估器上限，强制共识: {bias_removed_scores} -> 平均分 {consensus_score:.1f}")
                return self._create_result(bias_removed_scores, consensus_score, "forced_consensus", round_num)

    def _remove_max_bias(self, scores: List[int], remove_count: int) -> List[int]:
        """移除偏差最大的分数"""

        if len(scores) <= remove_count:
            raise ValueError(f"无法从 {len(scores)} 个评分中移除 {remove_count} 个")

        median_score = statistics.median(scores)

        # 计算每个分数与中位数的偏差（更科学）
        biases = [abs(score - median_score) for score in scores]

        # 按偏差从小到大排序，保留偏差较小的
        scored_scores = list(zip(scores, biases))
        scored_scores.sort(key=lambda x: x[1])

        # 移除偏差最大的几个分数
        kept_scores = [score for score, _ in scored_scores[:-remove_count]]

        print(f"🎯 偏差分析: 中位数={median_score:.2f}, 移除偏差最大的{remove_count}个分数")
        print(f"   偏差详情: {[(f'{s}(偏差{b:.2f})') for s, b in scored_scores]}")

        return kept_scores

    def _create_result(self, scores: List[int], consensus_score: float,
                      method: str, round_num: int) -> Dict[str, Any]:
        """创建共识结果"""

        return {
            'consensus_score': round(consensus_score, 2),
            'final_scores': scores,
            'evaluator_count': len(scores),
            'consensus_method': method,
            'processing_rounds': round_num,
            'score_distribution': dict(Counter(scores)),
            'quality_metrics': self._calculate_quality_metrics(scores)
        }

    def _calculate_quality_metrics(self, scores: List[int]) -> Dict[str, Any]:
        """计算质量指标"""

        if len(scores) < 2:
            return {'consensus_strength': 1.0, 'agreement_level': 'perfect'}

        # 共识强度（基于标准差）
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        consensus_strength = max(0.0, 1.0 - (std_dev / 2.0))

        # 同意程度
        max_count = max(Counter(scores).values())
        agreement_ratio = max_count / len(scores)

        if agreement_ratio >= 0.8:
            agreement_level = 'high'
        elif agreement_ratio >= 0.6:
            agreement_level = 'medium'
        else:
            agreement_level = 'low'

        return {
            'consensus_strength': round(consensus_strength, 3),
            'agreement_level': agreement_level,
            'agreement_ratio': round(agreement_ratio, 3),
            'evaluator_diversity': len(set(scores))
        }


def demo_adaptive_consensus():
    """演示自适应共识算法"""

    print("🧠 智能适应性共识算法演示")
    print("=" * 60)

    algorithm = AdaptiveConsensusAlgorithm()

    # 模拟获取额外评估器评分的函数
    def mock_additional_scores(count: int) -> List[int]:
        """模拟额外评估器评分"""
        # 为了演示，随机生成评分，但倾向于已有评分的众数
        available_scores = [1, 3, 5]
        weights = [0.2, 0.6, 0.2]  # 倾向于给3分
        return random.choices(available_scores, weights=weights, k=count)

    # 测试场景
    test_scenarios = [
        {
            'name': '完全共识',
            'scores': [3, 3, 3]
        },
        {
            'name': '轻微分歧',
            'scores': [3, 3, 5]
        },
        {
            'name': '严重分歧',
            'scores': [1, 3, 3]
        },
        {
            'name': '极端分歧',
            'scores': [1, 1, 5]
        }
    ]

    for scenario in test_scenarios:
        print(f"\n📊 测试场景: {scenario['name']}")
        print(f"初始评分: {scenario['scores']}")
        print("-" * 40)

        result = algorithm.adaptive_consensus(scenario['scores'], mock_additional_scores)

        print(f"\n📋 共识结果:")
        print(f"  共识评分: {result['consensus_score']}")
        print(f"  最终评分: {result['final_scores']}")
        print(f"  评估器数量: {result['evaluator_count']}")
        print(f"  共识方法: {result['consensus_method']}")
        print(f"  处理轮数: {result['processing_rounds']}")
        print(f"  质量指标: {result['quality_metrics']}")
        print()


if __name__ == "__main__":
    demo_adaptive_consensus()