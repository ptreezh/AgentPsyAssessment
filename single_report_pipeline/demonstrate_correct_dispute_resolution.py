#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确的争议解决流程演示
展示包含初始轮的3轮争议解决机制
"""

import sys
import os
import statistics
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .reverse_scoring_processor import ReverseScoringProcessor


def demonstrate_correct_dispute_resolution():
    """演示正确的争议解决流程"""
    print("正确的争议解决流程演示（3轮包含初始轮）")
    print("="*80)
    
    # 创建处理器实例
    processor = ReverseScoringProcessor()
    
    print("模拟一个存在争议的题目:")
    print("  题目ID: AGENT_B5_C6")
    print("  概念: C6: (Reversed) 我经常忘记把东西放回原处")
    print("  回答: '我会将物品放回原位。'")
    print()
    
    # 模拟完整的争议解决流程（总共3轮，包含初始轮）
    
    print("争议解决流程:")
    print("  总共3轮: 初始轮 + 2轮争议解决")
    print()
    
    # 第0轮：初始评估（3个主要模型）
    print("第0轮 (初始评估):")
    initial_scores = [1, 3, 5]  # 存在分歧的评分
    print(f"  评分: {initial_scores}")
    initial_reliability = processor.calculate_trait_reliability(initial_scores)
    initial_severity = processor.assess_dispute_severity(initial_scores)
    print(f"  可靠性: {initial_reliability:.3f}")
    print(f"  争议严重程度: {initial_severity}")
    print()
    
    # 检查是否需要争议解决
    if initial_severity in ['high', 'medium']:
        print("需要争议解决!")
        print(f"  评分范围: {max(initial_scores) - min(initial_scores)}")
        print(f"  评分标准差: {statistics.stdev(initial_scores):.2f}")
        print()
        
        # 第1轮争议解决（追加2个模型）
        print("第1轮争议解决:")
        round1_scores = [1, 1]  # 追加的评分（都支持高尽责性）
        print(f"  追加模型评分: {round1_scores}")
        
        # 更新总评分
        updated_scores_after_round1 = initial_scores + round1_scores
        print(f"  更新后评分: {updated_scores_after_round1}")
        
        # 检查是否可以提前终止（评分差别 <= 2，且4:1多数意见）
        score_range = max(updated_scores_after_round1) - min(updated_scores_after_round1)
        if score_range <= 2:
            from collections import Counter
            score_counts = Counter(updated_scores_after_round1)
            counts = list(score_counts.values())
            if len(counts) >= 2:
                max_count = max(counts)
                min_count = min(counts)
                if max_count >= 4 and min_count <= 1:
                    # 检测到4:1多数意见
                    majority_score = [score for score, count in score_counts.items() if count >= 4][0]
                    minority_score = [score for score, count in score_counts.items() if count <= 1][0]
                    print(f"  检测到4:1多数意见 ({majority_score}:4 vs {minority_score}:1)")
                    print(f"  评分差别 <= 2 且存在多数意见，提前终止争议解决")
                    final_scores = [majority_score] * 5  # 使用多数意见作为最终评分
                    print(f"  最终评分: {final_scores}")
                    print()
                    return  # 提前结束
        
        # 计算更新后的信度
        updated_reliability = processor.calculate_trait_reliability(updated_scores_after_round1)
        updated_severity = processor.assess_dispute_severity(updated_scores_after_round1)
        print(f"  更新后可靠性: {updated_reliability:.3f}")
        print(f"  更新后争议严重程度: {updated_severity}")
        print()
        
        # 检查第1轮后是否仍有争议
        if updated_severity in ['high', 'medium']:
            print("仍有争议，进行第2轮解决:")
            
            # 第2轮争议解决（再追加2个模型）
            round2_scores = [1, 1]  # 追加的评分（都支持高尽责性）
            print(f"  追加模型评分: {round2_scores}")
            
            # 更新总评分
            final_scores_all = updated_scores_after_round1 + round2_scores
            print(f"  最终总评分: {final_scores_all}")
            
            # 再次检查多数意见
            score_range_final = max(final_scores_all) - min(final_scores_all)
            if score_range_final <= 2:
                from collections import Counter
                final_score_counts = Counter(final_scores_all)
                final_counts = list(final_score_counts.values())
                if len(final_counts) >= 2:
                    max_final_count = max(final_counts)
                    min_final_count = min(final_counts)
                    if max_final_count >= 4 and min_final_count <= 1:
                        majority_final_score = [score for score, count in final_score_counts.items() if count >= 4][0]
                        minority_final_score = [score for score, count in final_score_counts.items() if count <= 1][0]
                        print(f"  检测到5:2多数意见 ({majority_final_score}:5 vs {minority_final_score}:2)")
                        print(f"  评分差别 <= 2 且存在多数意见，争议解决完成")
                        
                        # 使用多数意见作为最终评分
                        final_scores = [majority_final_score] * 7  # 7个模型中的5个支持
                        print(f"  最终评分: {final_scores}")
                        print()
                        return  # 结束争议解决
            
            # 计算最终信度
            final_reliability = processor.calculate_trait_reliability(final_scores_all)
            final_severity = processor.assess_dispute_severity(final_scores_all)
            print(f"  最终可靠性: {final_reliability:.3f}")
            print(f"  最终争议严重程度: {final_severity}")
            
            # 应用多数决策原则
            final_median = int(statistics.median(final_scores_all))
            final_mean = statistics.mean(final_scores_all)
            print(f"  中位数: {final_median}")
            print(f"  平均数: {final_mean:.2f}")
            
            # 确保最终评分是有效的1,3,5分
            if final_median not in [1, 3, 5]:
                if final_median <= 2:
                    final_score = 1
                elif final_median >= 4:
                    final_score = 5
                else:
                    final_score = 3
            else:
                final_score = final_median
            
            print(f"  最终原始评分: {final_score}")
            
            # 应用反向计分转换（因为是反向题目）
            final_adjusted_score = processor.reverse_score(final_score)
            print(f"  反向计分转换: {final_score} → {final_adjusted_score}")
            print(f"  最终调整后评分: {final_adjusted_score} (高尽责性)")
            print()
        else:
            print("第1轮后争议已解决")
            
            # 应用多数决策原则
            round1_median = int(statistics.median(updated_scores_after_round1))
            if round1_median not in [1, 3, 5]:
                if round1_median <= 2:
                    round1_final_score = 1
                elif round1_median >= 4:
                    round1_final_score = 5
                else:
                    round1_final_score = 3
            else:
                round1_final_score = round1_median
            
            print(f"  第1轮最终评分: {round1_final_score}")
            
            # 应用反向计分转换
            round1_adjusted_score = processor.reverse_score(round1_final_score)
            print(f"  反向计分转换: {round1_final_score} → {round1_adjusted_score}")
            print(f"  最终调整后评分: {round1_adjusted_score} (高尽责性)")
            print()
    else:
        print("无重大争议，无需争议解决")
        
        # 应用多数决策原则
        initial_median = int(statistics.median(initial_scores))
        print(f"  中位数: {initial_median}")
        
        # 应用反向计分转换
        if initial_median not in [1, 3, 5]:
            if initial_median <= 2:
                final_score = 1
            elif initial_median >= 4:
                final_score = 5
            else:
                final_score = 3
        else:
            final_score = initial_median
        
        # 应用反向计分转换（因为是反向题目）
        final_adjusted_score = processor.reverse_score(final_score)
        print(f"  反向计分转换: {final_score} → {final_adjusted_score}")
        print(f"  最终调整后评分: {final_adjusted_score}")
        print()
    
    # 最终总结
    print("争议解决流程总结:")
    print("="*60)
    print("  轮次: 3轮 (初始轮 + 2轮争议解决)")
    print("  模型总数: 7个 (3初始 + 2×2争议解决)")
    print("  解决策略: 分层多数决策 + 多数意见提前终止")
    print("  信度验证: 可靠性系数 + 严重程度评估")
    print("  置信度: 最终结果验证 + 改进评估")
    print()

def demonstrate_no_conflict_case():
    """演示无冲突案例"""
    print("\n无冲突案例演示:")
    print("="*60)
    
    processor = ReverseScoringProcessor()
    
    # 模拟一个高一致性的题目
    consistent_scores = [3, 3, 3]  # 高一致性评分
    print(f"初始评分: {consistent_scores}")
    
    # 计算信度
    reliability = processor.calculate_trait_reliability(consistent_scores)
    severity = processor.assess_dispute_severity(consistent_scores)
    print(f"可靠性: {reliability:.3f}")
    print(f"争议严重程度: {severity}")
    
    if severity == 'low':
        print("无重大争议，无需追加模型")
        median_score = int(statistics.median(consistent_scores))
        print(f"最终评分: {median_score}")
    print()

def demonstrate_minority_opinion_resolution():
    """演示少数意见解决"""
    print("\n少数意见解决演示:")
    print("="*60)
    
    processor = ReverseScoringProcessor()
    
    # 模拟评分分布：4个支持高分，1个支持低分
    scores_with_majority = [1, 1, 1, 1, 5]  # 4:1分布
    print(f"评分: {scores_with_majority}")
    
    # 检查评分范围
    score_range = max(scores_with_majority) - min(scores_with_majority)
    print(f"评分范围: {score_range}")
    
    if score_range <= 2:
        from collections import Counter
        score_counts = Counter(scores_with_majority)
        counts = list(score_counts.values())
        max_count = max(counts)
        min_count = min(counts)
        print(f"评分计数: {dict(score_counts)}")
        
        if max_count >= 4 and min_count <= 1:
            majority_score = [score for score, count in score_counts.items() if count >= 4][0]
            minority_score = [score for score, count in score_counts.items() if count <= 1][0]
            print(f"检测到4:1多数意见 ({majority_score}:4 vs {minority_score}:1)")
            print("评分差别 <= 2 且存在多数意见，无需追加模型")
            print(f"最终评分: {majority_score} (基于多数意见)")
        else:
            print("虽有分歧但无明显多数意见")
    else:
        print("评分差别 > 2，需要追加模型")
    
    print()


def main():
    """主函数"""
    demonstrate_correct_dispute_resolution()
    demonstrate_no_conflict_case()
    demonstrate_minority_opinion_resolution()
    
    print("正确的争议解决流程演示完成!")


if __name__ == "__main__":
    main()