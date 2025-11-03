#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版争议解决流水线
完整实现信度验证和置信度评估的分层争议解决策略
"""

import sys
import os
import statistics
from collections import Counter, defaultdict
from typing import Dict, List, Any
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .reverse_scoring_processor import ReverseScoringProcessor


class EnhancedDisputeResolutionPipeline:
    """增强版争议解决流水线"""
    
    def __init__(self):
        self.processor = ReverseScoringProcessor()
        self.max_rounds = 3  # 包含初始轮的总共3轮
        self.models_per_round = 2  # 每轮追加2个模型
    
    def calculate_trait_reliability(self, scores: List[int]) -> float:
        """计算特质可靠性"""
        return self.processor.calculate_trait_reliability(scores)
    
    def assess_dispute_severity(self, scores: List[int]) -> str:
        """评估争议严重程度"""
        return self.processor.assess_dispute_severity(scores)
    
    def validate_resolution_confidence(self, original_scores: List[int], 
                                     resolved_scores: List[int]) -> Dict[str, Any]:
        """验证解决置信度"""
        # 简化版本的置信度验证（在实际实现中会更复杂）
        if len(original_scores) < 2 or len(resolved_scores) < 2:
            return {
                'confidence': 0.5,
                'improvement': 0.0,
                'reliability_gain': 0.0,
                'original_reliability': 0.5,
                'resolved_reliability': 0.5
            }
        
        original_reliability = self.calculate_trait_reliability(original_scores)
        resolved_reliability = self.calculate_trait_reliability(resolved_scores)
        reliability_gain = resolved_reliability - original_reliability
        
        # 计算改善度
        original_range = max(original_scores) - min(original_scores) if original_scores else 0
        resolved_range = max(resolved_scores) - min(resolved_scores) if resolved_scores else 0
        improvement = original_range - resolved_range
        
        # 计算置信度
        confidence = 0.5  # 基础置信度
        if improvement > 0:
            confidence += 0.3 * min(1.0, improvement / 2.0)  # 范围改善贡献
        if reliability_gain > 0:
            confidence += 0.2 * min(1.0, reliability_gain / 0.3)  # 信度改善贡献
        
        return {
            'confidence': round(max(0.0, min(1.0, confidence)), 2),
            'improvement': round(improvement, 2),
            'reliability_gain': round(reliability_gain, 3),
            'original_reliability': round(original_reliability, 3),
            'resolved_reliability': round(resolved_reliability, 3)
        }
    
    def check_majority_opinion(self, all_scores: List[int]) -> Dict:
        """
        检查多数意见
        
        Args:
            all_scores: 所有评分列表
            
        Returns:
            多数意见信息或None
        """
        if not all_scores:
            return None
            
        score_range = max(all_scores) - min(all_scores)
        if score_range > 2:  # 评分差别太大，不考虑多数意见
            return None
            
        score_counts = Counter(all_scores)
        counts = list(score_counts.values())
        
        if len(counts) >= 2:
            max_count = max(counts)
            min_count = min(counts)
            
            # 检查是否存在明显的多数意见（如4:1, 5:1, 5:2等）
            if max_count >= 4 and min_count <= 1:
                majority_score = [score for score, count in score_counts.items() if count >= 4][0]
                minority_score = [score for score, count in score_counts.items() if count <= 1][0]
                return {
                    'majority_score': majority_score,
                    'minority_score': minority_score,
                    'ratio': f"{max_count}:{min_count}",
                    'counts': dict(score_counts)
                }
        
        return None
    
    def resolve_single_trait(self, scores_list: List[int], 
                            primary_dimension: str = None) -> Dict:
        """
        解决单个特质的争议
        
        Args:
            scores_list: 评分列表
            primary_dimension: 主要维度
            
        Returns:
            解决结果
        """
        print(f"  解决特质争议: {primary_dimension or 'Unknown'}")
        print(f"    初始评分: {scores_list}")
        
        # 计算初始信度和严重程度
        initial_reliability = self.calculate_trait_reliability(scores_list)
        initial_severity = self.assess_dispute_severity(scores_list)
        print(f"    初始可靠性: {initial_reliability:.3f}, 严重程度: {initial_severity}")
        
        # 检查是否需要解决
        if initial_severity == 'low':
            # 低争议，直接使用多数决策
            median_score = int(statistics.median(scores_list))
            print(f"    低争议，直接使用中位数: {median_score}")
            return {
                'final_score': median_score,
                'reliability': initial_reliability,
                'severity': initial_severity,
                'resolution_rounds': 0,
                'total_scores': len(scores_list),
                'confidence': 0.8  # 高置信度
            }
        
        # 高争议，需要追加模型
        current_scores = scores_list.copy()
        resolution_round = 0
        all_resolved_scores = [scores_list]
        
        # 迭代解决争议
        while resolution_round < (self.max_rounds - 1):  # 最多2轮追加模型
            print(f"    第 {resolution_round + 1} 轮争议解决:")
            
            # 追加模型评分（每轮2个模型）
            round_scores = []
            for i in range(self.models_per_round):
                # 模拟追加模型评分（这里简化处理）
                # 在实际应用中，这里会调用实际的模型
                added_score = int(statistics.median(current_scores))
                round_scores.append(added_score)
            
            print(f"      追加评分: {round_scores}")
            
            # 更新总评分
            current_scores.extend(round_scores)
            all_resolved_scores.append(round_scores)
            print(f"      更新后总评分: {current_scores}")
            
            # 检查多数意见
            majority_info = self.check_majority_opinion(current_scores)
            if majority_info:
                print(f"      检测到多数意见: {majority_info['majority_score']} ({majority_info['ratio']})")
                print(f"      提前终止争议解决")
                return {
                    'final_score': majority_info['majority_score'],
                    'reliability': self.calculate_trait_reliability(current_scores),
                    'severity': self.assess_dispute_severity(current_scores),
                    'resolution_rounds': resolution_round + 1,
                    'total_scores': len(current_scores),
                    'confidence': 0.95,  # 多数意见高置信度
                    'majority_opinion': majority_info
                }
            
            # 计算更新后的信度
            current_reliability = self.calculate_trait_reliability(current_scores)
            current_severity = self.assess_dispute_severity(current_scores)
            print(f"      更新后可靠性: {current_reliability:.3f}, 严重程度: {current_severity}")
            
            # 检查是否可以终止
            if current_severity == 'low':
                print(f"      争议已解决")
                median_score = int(statistics.median(current_scores))
                return {
                    'final_score': median_score,
                    'reliability': current_reliability,
                    'severity': current_severity,
                    'resolution_rounds': resolution_round + 1,
                    'total_scores': len(current_scores),
                    'confidence': 0.9  # 解决后高置信度
                }
            
            resolution_round += 1
        
        # 最终使用多数决策
        final_median = int(statistics.median(current_scores))
        final_reliability = self.calculate_trait_reliability(current_scores)
        final_severity = self.assess_dispute_severity(current_scores)
        
        print(f"    达到最大轮次，使用最终中位数: {final_median}")
        return {
            'final_score': final_median,
            'reliability': final_reliability,
            'severity': final_severity,
            'resolution_rounds': resolution_round,
            'total_scores': len(current_scores),
            'confidence': 0.85  # 多轮解决后较高置信度
        }
    
    def demonstrate_enhanced_resolution(self):
        """演示增强的争议解决流程"""
        print("增强版争议解决流水线演示")
        print("="*60)
        
        # 案例1：高争议题目
        print("案例1: 高争议题目解决")
        high_conflict_scores = [1, 3, 5]  # 存在严重分歧
        result1 = self.resolve_single_trait(high_conflict_scores, 'Conscientiousness')
        print(f"  解决结果: {result1}")
        print()
        
        # 案例2：中等争议题目
        print("案例2: 中等争议题目解决")
        medium_conflict_scores = [1, 1, 3, 3, 5]  # 中等分歧
        result2 = self.resolve_single_trait(medium_conflict_scores, 'Extraversion')
        print(f"  解决结果: {result2}")
        print()
        
        # 案例3：多数意见题目
        print("案例3: 多数意见题目解决")
        majority_opinion_scores = [1, 1, 1, 1, 5]  # 4:1多数意见
        result3 = self.resolve_single_trait(majority_opinion_scores, 'Agreeableness')
        print(f"  解决结果: {result3}")
        print()
        
        # 案例4：无争议题目
        print("案例4: 无争议题目解决")
        no_conflict_scores = [3, 3, 3]  # 高一致性
        result4 = self.resolve_single_trait(no_conflict_scores, 'Neuroticism')
        print(f"  解决结果: {result4}")
        print()
        
        print("增强争议解决流水线演示完成!")
        print("="*60)
        
        return [result1, result2, result3, result4]


def main():
    """主函数"""
    pipeline = EnhancedDisputeResolutionPipeline()
    results = pipeline.demonstrate_enhanced_resolution()
    
    # 显示汇总统计
    print("\n汇总统计:")
    print("--------")
    total_rounds = sum(r['resolution_rounds'] for r in results)
    avg_confidence = statistics.mean(r['confidence'] for r in results if 'confidence' in r)
    
    print(f"总解决轮次: {total_rounds}")
    print(f"平均置信度: {avg_confidence:.3f}")
    
    # 按严重程度分类
    severity_count = defaultdict(int)
    for r in results:
        severity = r.get('severity', 'unknown')
        severity_count[severity] += 1
    
    print("\n争议严重程度分布:")
    for severity, count in severity_count.items():
        print(f"  {severity}: {count}")


if __name__ == "__main__":
    main()