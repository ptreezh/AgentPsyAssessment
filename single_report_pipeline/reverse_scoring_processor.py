#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反向计分处理模块
处理大五人格测评中的反向计分题目
"""

from typing import Dict, List
import statistics
from collections import Counter


class ReverseScoringProcessor:
    """反向计分处理器"""
    
    def __init__(self):
        # 定义反向计分题目的映射，基于IPIP量表
        self.reverse_scoring_items = {
            # 神经质 (Neuroticism) - 反向: N1, N4, N6, N8
            'N1', 'N4', 'N6', 'N8',
            # 外向性 (Extraversion) - 反向: E5, E6, E7, E8, E9, E10  
            'E5', 'E6', 'E7', 'E8', 'E9', 'E10',
            # 宜人性 (Agreeableness) - 反向: A5, A6, A7, A8, A9, A10
            'A5', 'A6', 'A7', 'A8', 'A9', 'A10',
            # 尽责性 (Conscientiousness) - 反向: C5, C6, C7, C8, C9, C10
            'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
            # 开放性 (Openness) - 反向: O6, O7, O8, O9, O10
            'O6', 'O7', 'O8', 'O9', 'O10'
        }
    
    def is_reverse_item(self, item_id: str) -> bool:
        """
        检查题目是否为反向计分题
        
        Args:
            item_id: 题目ID，如 'AGENT_B5_C6'
            
        Returns:
            是否为反向计分题
        """
        # 从题目ID中提取维度和题号，例如 'AGENT_B5_C6' -> 'C6'
        if item_id.startswith('AGENT_B5_'):
            dimension_item = item_id.split('_')[-1]  # 取最后部分，如'C6'
            return dimension_item in self.reverse_scoring_items
        return False
    
    def is_reverse_from_concept(self, concept: str) -> bool:
        """
        根据概念描述判断是否为反向计分题
        
        Args:
            concept: 概念描述，如 'C10: (Reversed) 我做事没有条理'
            
        Returns:
            是否为反向计分题
        """
        return '(Reversed)' in concept or ': (Reversed)' in concept
    
    def reverse_score(self, score: int) -> int:
        """
        对分数进行反向处理 (1↔5, 3保持不变)
        
        Args:
            score: 原始分数 (1, 3, or 5)
            
        Returns:
            反向后的分数
        """
        if score == 1:
            return 5
        elif score == 5:
            return 1
        elif score == 3:
            return 3
        else:
            raise ValueError(f"无效的分数: {score}，只支持1, 3, 5分")
    
    def calculate_trait_reliability(self, trait_scores: List[int]) -> float:
        """
        计算单个特质的评分信度
        
        Args:
            trait_scores: 特质评分列表
            
        Returns:
            信度系数 (0-1之间)
        """
        if len(trait_scores) < 2:
            return 0.0
        
        # 使用简化的一致性指标
        # 1. 标准差越小，一致性越高
        std_dev = statistics.stdev(trait_scores)
        max_possible_std = 2.0  # 1-5评分制的最大标准差约为2
        consistency_score = max(0.0, 1.0 - (std_dev / max_possible_std))
        
        # 2. 众数比例越高，一致性越高
        score_counts = Counter(trait_scores)
        max_count = max(score_counts.values())
        mode_ratio = max_count / len(trait_scores)
        
        # 综合信度得分
        reliability = 0.6 * consistency_score + 0.4 * mode_ratio
        return round(reliability, 3)
    
    def assess_dispute_severity(self, scores: List[int]) -> str:
        """
        评估争议严重程度
        
        Args:
            scores: 评分列表
            
        Returns:
            争议严重程度 ('low', 'medium', 'high')
        """
        if len(scores) < 2:
            return 'low'
        
        score_range = max(scores) - min(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        mean_score = statistics.mean(scores)
        
        # 严重程度判断标准
        if score_range <= 1 and std_dev <= 0.5:
            return 'low'  # 轻微分歧
        elif score_range <= 2 and std_dev <= 1.0:
            return 'medium'  # 中等分歧
        else:
            return 'high'  # 严重分歧
    
    def validate_resolution_confidence(self, original_scores: List[int], 
                                      resolved_scores: List[int]) -> Dict:
        """
        验证解决结果置信度
        
        Args:
            original_scores: 原始评分
            resolved_scores: 解决后评分
            
        Returns:
            置信度评估结果
        """
        if len(original_scores) < 2:
            return {
                'confidence': 0.5,
                'improvement': 0.0,
                'reliability_gain': 0.0,
                'original_reliability': 0.5,
                'resolved_reliability': 0.5
            }
        
        # 1. 一致性改善
        original_range = max(original_scores) - min(original_scores) if original_scores else 0
        resolved_range = max(resolved_scores) - min(resolved_scores) if resolved_scores else 0
        improvement = original_range - resolved_range
        
        # 2. 信度提升
        original_reliability = self.calculate_trait_reliability(original_scores)
        resolved_reliability = self.calculate_trait_reliability(resolved_scores)
        reliability_gain = resolved_reliability - original_reliability
        
        # 3. 置信度综合评估
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
    
    def process_scores_for_big5_calculation(self, question_scores: List[Dict]) -> List[Dict]:
        """
        处理所有题目分数，对反向计分题进行反向处理
        
        Args:
            question_scores: 包含所有题目评分的列表
                格式：[
                    {
                        'question_id': 'AGENT_B5_C6',
                        'question_info': {...},
                        'scores': {'extraversion': 3, 'conscientiousness': 1, ...}
                    },
                    ...
                ]
            
        Returns:
            处理后的题目评分列表
        """
        processed_scores = []
        
        for item in question_scores:
            question_id = item.get('question_id', '')
            question_info = item.get('question_info', {})
            scores = item.get('scores', {})
            
            # 检查是否需要反向计分
            concept = question_info.get('question_data', {}).get('mapped_ipip_concept', '')
            is_reversed = self.is_reverse_item(question_id) or self.is_reverse_from_concept(concept)
            
            if is_reversed:
                # 根据题目维度确定需要反向的分数
                processed_item_scores = scores.copy()
                
                # 获取题目所属维度
                dimension = question_info.get('question_data', {}).get('dimension', '')
                if dimension:
                    # 将维度名转换为Big5标准名称
                    dimension_map = {
                        'Extraversion': 'extraversion',
                        'Agreeableness': 'agreeableness', 
                        'Conscientiousness': 'conscientiousness',
                        'Neuroticism': 'neuroticism',
                        'Openness to Experience': 'openness_to_experience'
                    }
                    
                    big5_dimension = dimension_map.get(dimension)
                    if big5_dimension and big5_dimension in processed_item_scores:
                        original_score = processed_item_scores[big5_dimension]
                        reversed_score = self.reverse_score(original_score)
                        processed_item_scores[big5_dimension] = reversed_score
                        
                        print(f"反向计分处理: 题目 {question_id} ({concept}) - {big5_dimension}: {original_score} → {reversed_score}")
                
                processed_scores.append({
                    **item,
                    'scores': processed_item_scores,
                    'is_reversed': True
                })
            else:
                processed_scores.append({
                    **item,
                    'scores': scores,
                    'is_reversed': False
                })
        
        return processed_scores
    
    def calculate_big5_scores(self, processed_scores: List[Dict]) -> Dict[str, float]:
        """
        计算大五人格各维度最终得分
        
        Args:
            processed_scores: 已处理反向计分的题目评分列表
            
        Returns:
            大五人格各维度平均分
        """
        # 按维度分组收集分数
        scores_by_dimension = {
            'openness_to_experience': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        }
        
        for item in processed_scores:
            scores = item.get('scores', {})
            for dimension in scores_by_dimension:
                if dimension in scores:
                    score = scores[dimension]
                    if score in [1, 3, 5]:  # 确保是有效分数
                        scores_by_dimension[dimension].append(score)
        
        # 计算各维度平均分
        big5_scores = {}
        for dimension, dimension_scores in scores_by_dimension.items():
            if dimension_scores:
                avg_score = sum(dimension_scores) / len(dimension_scores)
                big5_scores[dimension] = round(avg_score, 2)
            else:
                big5_scores[dimension] = 0.0  # 或者可以设置为3.0表示中性
        
        return big5_scores


def test_reverse_scoring():
    """测试反向计分功能"""
    processor = ReverseScoringProcessor()
    
    # 测试反向计分识别
    test_cases = [
        ('AGENT_B5_C6', True),   # 反向计分
        ('AGENT_B5_E1', False),  # 正向计分
        ('AGENT_B5_N6', True),   # 反向计分
    ]
    
    print("反向计分识别测试:")
    for item_id, expected in test_cases:
        result = processor.is_reverse_item(item_id)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {item_id}: {result} (期望: {expected})")
    
    # 测试分数反向
    print("\n分数反向测试:")
    test_scores = [1, 3, 5]
    for score in test_scores:
        reversed_score = processor.reverse_score(score)
        print(f"  {score} → {reversed_score}")
    
    # 测试处理完整数据
    print("\n完整数据处理测试:")
    sample_data = [
        {
            'question_id': 'AGENT_B5_C6',
            'question_info': {
                'question_data': {
                    'dimension': 'Conscientiousness',
                    'mapped_ipip_concept': 'C6: (Reversed) 我经常忘记把东西放回原处'
                }
            },
            'scores': {
                'extraversion': 3,
                'conscientiousness': 1,  # 反向题，1分表示高尽责性，应转为5分
                'agreeableness': 4,
                'conscientiousness': 1,
                'neuroticism': 3,
                'openness_to_experience': 3
            }
        },
        {
            'question_id': 'AGENT_B5_E1', 
            'question_info': {
                'question_data': {
                    'dimension': 'Extraversion',
                    'mapped_ipip_concept': 'E1: 我是团队活动的核心人物。'
                }
            },
            'scores': {
                'extraversion': 5,
                'conscientiousness': 3,
                'agreeableness': 4,
                'neuroticism': 2,
                'openness_to_experience': 4
            }
        }
    ]
    
    processed = processor.process_scores_for_big5_calculation(sample_data)
    print(f"处理后数据: {len(processed)} 题")
    for item in processed:
        qid = item['question_id']
        scores = item['scores']
        is_rev = item['is_reversed']
        print(f"  {qid} (反向: {is_rev}): {scores}")
    
    big5_scores = processor.calculate_big5_scores(processed)
    print(f"\n大五人格得分: {big5_scores}")


if __name__ == "__main__":
    test_reverse_scoring()