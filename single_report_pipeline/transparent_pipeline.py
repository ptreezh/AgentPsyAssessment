#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
透明化的单文件评估流水线
提供详细的每步反馈输出
"""

import json
import ollama
from typing import Dict, List, Any
from .context_generator import ContextGenerator
from .reverse_scoring_processor import ReverseScoringProcessor
from .input_parser import InputParser
import time
import statistics
import re


class TransparentPipeline:
    """透明化的单文件评估流水线"""
    
    def __init__(self, primary_models: List[str] = None, dispute_models: List[str] = None):
        """
        初始化流水线
        
        Args:
            primary_models: 主要评估模型列表
            dispute_models: 争议解决模型列表
        """
        self.primary_models = primary_models or [
            'qwen3:8b',
            'deepseek-r1:8b', 
            'mistral-nemo:latest'
        ]
        
        # 准备7个评估器模型，按品牌差异和尺度要求编排
        self.dispute_models = dispute_models or [
            'llama3:latest',      # Meta (第1轮第1个)
            'gemma3:latest',      # Google (第1轮第2个)
            'phi3:mini',          # Microsoft (第2轮第1个)
            'yi:6b',              # 01.AI (第2轮第2个)
            'qwen3:4b',           # Alibaba (第3轮第1个)
            'deepseek-r1:8b',     # DeepSeek (第3轮第2个)
            'mixtral:8x7b'        # Mistral (备用)
        ]
        
        self.context_generator = ContextGenerator()
        self.reverse_processor = ReverseScoringProcessor()
        self.input_parser = InputParser()
        self.max_dispute_rounds = 3
        self.dispute_threshold = 1.0
    
    def parse_scores_from_response(self, response: str) -> Dict[str, int]:
        """从模型响应中解析评分"""
        import json
        
        # 尝试查找JSON部分
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                if 'scores' in data:
                    scores = data['scores']
                    # 确保所有分数都是1、3、5中的一个
                    for trait, score in scores.items():
                        if isinstance(score, (int, float)):
                            if score <= 2:
                                scores[trait] = 1
                            elif score <= 4:
                                scores[trait] = 3
                            else:
                                scores[trait] = 5
                        else:
                            scores[trait] = 3  # 默认值
                    return scores
            except json.JSONDecodeError:
                pass
        
        # 如果找不到JSON，返回默认值
        return {
            'openness_to_experience': 3,
            'conscientiousness': 3,
            'extraversion': 3,
            'agreeableness': 3,
            'neuroticism': 3
        }
    
    def evaluate_single_question(self, context: str, model: str, question_id: str) -> Dict[str, int]:
        """
        使用单个模型评估单道题，并提供详细反馈
        """
        print(f"    └─ 使用模型 {model} 评估题目 {question_id}...")
        try:
            response = ollama.generate(model=model, prompt=context, options={'num_predict': 2000})
            scores = self.parse_scores_from_response(response['response'])
            print(f"      评分: {scores}")
            return scores
        except Exception as e:
            print(f"      ❌ 模型 {model} 评估失败: {e}")
            # 返回默认评分
            default_scores = {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
            print(f"      使用默认评分: {default_scores}")
            return default_scores
    
    def detect_disputes(self, scores_list: List[Dict[str, int]], threshold: float = 1.0) -> Dict[str, List]:
        """检测评分争议（所有维度）"""
        disputes = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            trait_scores = [scores[trait] for scores in scores_list if trait in scores]
            if len(trait_scores) > 1:
                score_range = max(trait_scores) - min(trait_scores)
                if score_range > threshold:
                    # 计算信度
                    reliability = self.reverse_processor.calculate_trait_reliability(trait_scores)
                    severity = self.reverse_processor.assess_dispute_severity(trait_scores)
                    
                    disputes[trait] = {
                        'scores': trait_scores,
                        'range': score_range,
                        'reliability': reliability,
                        'severity': severity,
                        'requires_resolution': True
                    }
        
        return disputes
    
    def detect_major_dimension_disputes(self, scores_list: List[Dict[str, int]], question: Dict, threshold: float = 1.0) -> Dict[str, List]:
        """检测主要维度评分争议（只检查题目所属的主要维度）"""
        # 获取题目主要维度
        question_data = question.get('question_data', {})
        primary_dimension = question_data.get('dimension', '')
        
        # 映射到标准维度名称
        dimension_map = {
            'Openness to Experience': 'openness_to_experience',
            'Conscientiousness': 'conscientiousness',
            'Extraversion': 'extraversion',
            'Agreeableness': 'agreeableness',
            'Neuroticism': 'neuroticism'
        }
        
        standard_primary_dimension = dimension_map.get(primary_dimension, '')
        
        if not standard_primary_dimension:
            # 如果无法确定主要维度，返回所有争议
            return self.detect_disputes(scores_list, threshold)
        
        # 只检查主要维度的争议
        disputes = {}
        trait_scores = [scores[standard_primary_dimension] for scores in scores_list if standard_primary_dimension in scores]
        if len(trait_scores) > 1:
            score_range = max(trait_scores) - min(trait_scores)
            if score_range > threshold:
                # 计算信度和严重程度
                reliability = self.reverse_processor.calculate_trait_reliability(trait_scores)
                severity = self.reverse_processor.assess_dispute_severity(trait_scores)
                
                disputes[standard_primary_dimension] = {
                    'scores': trait_scores,
                    'range': score_range,
                    'reliability': reliability,
                    'severity': severity,
                    'requires_resolution': True
                }
        
        return disputes
    
    def process_single_question(self, question: Dict, question_idx: int) -> Dict[str, Any]:
        """
        处理单道题，提供详细反馈
        """
        question_id = question.get('question_id', 'Unknown')
        question_concept = question['question_data'].get('mapped_ipip_concept', 'Unknown')
        
        # 确保question_id是字符串
        if not isinstance(question_id, str):
            question_id = str(question_id)
        
        is_reversed = self.reverse_processor.is_reverse_item(question_id) or \
                     self.reverse_processor.is_reverse_from_concept(question_concept)
        
        print(f"处理第 {question_idx+1:02d} 题 (ID: {question_id})")
        print(f"  题目概念: {question_concept}")
        print(f"  是否反向: {is_reversed}")
        print(f"  被试回答: {question['extracted_response'][:100]}...")
        
        # 生成评估上下文
        context = self.context_generator.generate_evaluation_prompt(question)
        
        # 初始评估（使用3个主要模型）
        print(f"  初始评估 (使用 {len(self.primary_models)} 个模型):")
        initial_scores = []
        for model in self.primary_models:
            scores = self.evaluate_single_question(context, model, question_id)
            initial_scores.append({
                'model': model,
                'scores': scores,
                'raw_scores': scores.copy()  # 保存原始评分
            })
            time.sleep(0.5)  # 防止API过载
        
        # 检查是否存在争议（只检查主要维度）
        all_initial_scores = [item['scores'] for item in initial_scores]
        disputes = self.detect_major_dimension_disputes(all_initial_scores, question, self.dispute_threshold)
        
        print(f"  争议检测: {len(disputes)} 个主要维度存在分歧")
        if disputes:
            for trait, dispute_info in disputes.items():
                print(f"    - {trait}: 评分 {dispute_info['scores']}, 差距 {dispute_info['range']}")
        else:
            print(f"    无重大分歧")
        
        # 争议解决（总共3轮，包含初始轮）
        current_scores = initial_scores.copy()
        resolution_round = 0
        all_models_used = [item['model'] for item in initial_scores]
        all_scores_data = all_initial_scores.copy()
        
        # 第一轮就是初始评估，所以从第0轮开始计数
        # 总共允许3轮：初始轮 + 2轮争议解决 = 3轮总计
        
        while disputes and resolution_round < 2:  # 最多2轮额外争议解决
            print(f"  第 {resolution_round + 1} 轮争议解决:")
            
            # 获取当前争议的严重程度
            max_severity = 'low'
            for trait, dispute_info in disputes.items():
                severity = dispute_info.get('severity', 'medium')
                if severity == 'high':
                    max_severity = 'high'
                    break
                elif severity == 'medium':
                    max_severity = 'medium'
            
            print(f"    争议严重程度: {max_severity}")
            
            # 每轮使用2个争议解决模型追加评估
            dispute_models_for_round = []
            for i in range(2):  # 每轮2个模型
                model_index = (resolution_round * 2 + i) % len(self.dispute_models)
                dispute_models_for_round.append(self.dispute_models[model_index])
            
            print(f"    使用追加模型: {dispute_models_for_round}")
            
            # 为每轮的2个模型进行评估
            new_scores_for_round = []
            for dispute_model in dispute_models_for_round:
                print(f"    使用模型 {dispute_model}:")
                new_scores = self.evaluate_single_question(context, dispute_model, question_id)
                
                # 添加到评分记录
                current_scores.append({
                    'model': dispute_model,
                    'scores': new_scores,
                    'raw_scores': new_scores.copy()
                })
                all_models_used.append(dispute_model)
                all_scores_data.append(new_scores)
                new_scores_for_round.append(new_scores)
            
            # 应用分层争议解决策略
            if new_scores_for_round:
                # 根据严重程度决定解决策略
                if max_severity == 'high':
                    # 严重分歧：使用高权重解决策略
                    print(f"    应用高严重程度解决策略")
                elif max_severity == 'medium':
                    # 中等分歧：使用中等权重解决策略
                    print(f"    应用中等严重程度解决策略")
                else:
                    # 轻微分歧：使用基础解决策略
                    print(f"    应用低严重程度解决策略")
            
            # 重新检测争议（只检查主要维度）
            major_disputes = self.detect_major_dimension_disputes(all_scores_data, question, self.dispute_threshold)
            
            # 检查是否可以提前终止争议解决
            can_terminate = False
            if major_disputes:
                for trait, dispute_info in major_disputes.items():
                    scores = dispute_info['scores']
                    score_range = dispute_info['range']
                    
                    # 如果评分差别 <= 2，且有4:1的多数意见，则无冲突
                    if score_range <= 2:
                        from collections import Counter
                        score_counts = Counter(scores)
                        counts = list(score_counts.values())
                        if len(counts) >= 2 and max(counts) >= 4 and min(counts) <= 1:
                            # 4:1多数意见
                            majority_score = [score for score, count in score_counts.items() if count >= 4][0]
                            minority_score = [score for score, count in score_counts.items() if count <= 1][0]
                            print(f"    检测到4:1多数意见 ({majority_score}:4 vs {minority_score}:1)，提前终止争议解决")
                            can_terminate = True
                            # 直接使用多数意见作为最终评分
                            for i, score_data in enumerate(all_scores_data):
                                if trait in score_data:
                                    all_scores_data[i][trait] = majority_score
            
            if not can_terminate:
                disputes = major_disputes
                resolution_round += 1
                
                # 计算解决后的置信度
                if disputes:
                    print(f"    仍存在 {len(disputes)} 个主要维度分歧: {list(disputes.keys())}")
                    # 显示每个争议的详细信息
                    for trait, dispute_info in disputes.items():
                        reliability = dispute_info.get('reliability', 0.0)
                        severity = dispute_info.get('severity', 'medium')
                        print(f"      {trait}: 可靠性={reliability:.3f}, 严重程度={severity}")
                else:
                    print(f"    所有主要维度分歧已解决")
                
                # 显示本轮解决效果
                current_trait_scores = {}
                for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    trait_scores = [scores[trait] for scores in all_scores_data if trait in scores]
                    if trait_scores:
                        current_trait_scores[trait] = trait_scores
                
                print(f"    当前评分分布:")
                for trait, scores in current_trait_scores.items():
                    if scores:
                        mean_score = statistics.mean(scores)
                        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                        reliability = self.reverse_processor.calculate_trait_reliability(scores)
                        print(f"      {trait}: 均值={mean_score:.2f}, 标准差={std_dev:.2f}, 可靠性={reliability:.3f}")
            else:
                # 提前终止争议解决
                disputes = {}  # 清空争议，结束循环
                resolution_round += 1
                print(f"    基于多数意见提前终止争议解决")
        
        # 应用多数决策原则确定最终原始评分
        final_raw_scores = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        # 收集所有评分数据用于置信度验证
        all_trait_scores = {}
        for trait in traits:
            trait_scores = [scores_data[trait] for scores_data in all_scores_data if trait in scores_data]
            all_trait_scores[trait] = trait_scores
        
        for trait in traits:
            trait_scores = all_trait_scores[trait]
            if trait_scores:
                # 使用中位数作为最终评分
                median_score = statistics.median(trait_scores)
                final_raw_scores[trait] = int(round(median_score))  # 确保是整数
                
                # 计算该特质的信度
                reliability = self.reverse_processor.calculate_trait_reliability(trait_scores)
                print(f"    {trait}: 评分={final_raw_scores[trait]}, 可靠性={reliability:.3f}, 样本数={len(trait_scores)}")
            else:
                final_raw_scores[trait] = 3  # 默认值
                print(f"    {trait}: 无评分数据，使用默认值3")
        
        print(f"  原始最终评分: {final_raw_scores}")
        
        # 应用反向计分转换（如果需要）
        if is_reversed:
            final_adjusted_scores = {}
            print(f"  应用反向计分转换:")
            for trait, raw_score in final_raw_scores.items():
                adjusted_score = self.reverse_processor.reverse_score(raw_score)
                final_adjusted_scores[trait] = adjusted_score
                if raw_score != adjusted_score:
                    print(f"    {trait}: {raw_score} → {adjusted_score}")
                else:
                    print(f"    {trait}: {raw_score} (不变)")
        else:
            final_adjusted_scores = final_raw_scores
            print(f"  非反向题目，无需转换: {final_adjusted_scores}")
        
        # 计算整体置信度
        overall_reliability = statistics.mean([
            self.reverse_processor.calculate_trait_reliability(all_trait_scores[trait])
            for trait in traits if all_trait_scores[trait]
        ]) if any(all_trait_scores[trait] for trait in traits) else 0.0
        
        print(f"  最终评分: {final_adjusted_scores}")
        print(f"  整体可靠性: {overall_reliability:.3f}")
        print(f"  使用模型: {all_models_used}")
        print(f"  争议解决轮次: {resolution_round}")
        print(f"  评分总数: {len(all_scores_data)}")
        print()
        
        return {
            'question_id': question_id,
            'question_info': question,
            'initial_scores': initial_scores,
            'final_raw_scores': final_raw_scores,
            'final_adjusted_scores': final_adjusted_scores,
            'resolution_rounds': resolution_round,
            'disputes_initial': len(self.detect_disputes([item['scores'] for item in initial_scores])),
            'disputes_final': len(disputes),
            'models_used': all_models_used,
            'is_reversed': is_reversed,
            'scores_data': all_scores_data,
            'confidence_metrics': {
                'overall_reliability': round(overall_reliability, 3),
                'trait_reliabilities': {
                    trait: self.reverse_processor.calculate_trait_reliability(all_trait_scores[trait])
                    for trait in traits if all_trait_scores[trait]
                }
            }
        }
    
    def calculate_big5_scores(self, question_results: List[Dict]) -> Dict[str, float]:
        """计算大五人格各维度得分（带权重）"""
        print("开始计算大五人格得分（带权重）:")
        
        # 按维度收集分数和权重
        scores_by_dimension = {
            'openness_to_experience': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        }
        
        # 收集每道题的主要维度信息
        for result in question_results:
            scores = result['final_adjusted_scores']  # 使用调整后分数
            question_info = result.get('question_info', {})
            question_data = question_info.get('question_data', {})
            primary_dimension = question_data.get('dimension', '')  # 题目主要维度
            
            # 将主要维度映射到标准名称
            dimension_map = {
                'Openness to Experience': 'openness_to_experience',
                'Conscientiousness': 'conscientiousness',
                'Extraversion': 'extraversion',
                'Agreeableness': 'agreeableness',
                'Neuroticism': 'neuroticism'
            }
            
            standard_primary_dimension = dimension_map.get(primary_dimension, '')
            
            # 为每个维度添加带权重的分数
            for dimension in scores_by_dimension:
                if dimension in scores:
                    score = scores[dimension]
                    if score in [1, 3, 5]:  # 确保是有效分数
                        # 计算权重：主要维度70%，其他维度各7.5%
                        if dimension == standard_primary_dimension and standard_primary_dimension:
                            weight = 0.7  # 主要维度高权重
                        else:
                            weight = 0.075  # 其他维度低权重
                        
                        scores_by_dimension[dimension].append({
                            'score': score,
                            'weight': weight,
                            'is_primary': (dimension == standard_primary_dimension and standard_primary_dimension)
                        })
        
        # 计算加权平均分
        big5_scores = {}
        for dimension, weighted_scores in scores_by_dimension.items():
            if weighted_scores:
                # 计算加权平均
                total_weighted_score = sum(item['score'] * item['weight'] for item in weighted_scores)
                total_weight = sum(item['weight'] for item in weighted_scores)
                
                if total_weight > 0:
                    weighted_avg = total_weighted_score / total_weight
                    big5_scores[dimension] = round(weighted_avg, 2)
                    
                    # 统计信息
                    primary_scores = [item['score'] for item in weighted_scores if item['is_primary']]
                    other_scores = [item['score'] for item in weighted_scores if not item['is_primary']]
                    
                    print(f"  {dimension}:")
                    if primary_scores:
                        primary_avg = sum(primary_scores) / len(primary_scores)
                        print(f"    主要维度平均: {primary_avg:.2f} (n={len(primary_scores)})")
                    if other_scores:
                        other_avg = sum(other_scores) / len(other_scores)
                        print(f"    其他维度平均: {other_avg:.2f} (n={len(other_scores)})")
                    print(f"    加权总分: {weighted_avg:.2f}")
                else:
                    big5_scores[dimension] = 3.0  # 默认中性分
            else:
                print(f"  {dimension}: 无评分数据")
                big5_scores[dimension] = 3.0  # 默认中性分
        
        return big5_scores
    
    def calculate_mbti_type(self, big5_scores: Dict[str, float]) -> str:
        """基于大五分数推断MBTI类型"""
        # 简化的MBTI推断逻辑
        O = big5_scores.get('openness_to_experience', 3)
        C = big5_scores.get('conscientiousness', 3)
        E = big5_scores.get('extraversion', 3)
        A = big5_scores.get('agreeableness', 3)
        N = big5_scores.get('neuroticism', 3)
        
        # E/I: 外向性 vs 神经质
        e_score = E + (5 - N)  # 高外向性+低神经质=更外向
        i_score = (5 - E) + N
        E_preference = 'E' if e_score > i_score else 'I'
        
        # S/N: 感觉 vs 直觉 (基于开放性)
        S_preference = 'S' if O <= 3 else 'N'
        
        # T/F: 思考 vs 情感 (基于宜人性)
        T_preference = 'T' if A <= 3 else 'F'
        
        # J/P: 判断 vs 知觉 (基于尽责性)
        J_preference = 'J' if C > 3 else 'P'
        
        mbti_type = f"{E_preference}{S_preference}{T_preference}{J_preference}"
        print(f"推断MBTI类型: {mbti_type}")
        print(f"  E/I: E({E}) vs I({5-E}) + N({N}) → {E_preference}")
        print(f"  S/N: O({O}) → {S_preference}")
        print(f"  T/F: A({A}) → {T_preference}")
        print(f"  J/P: C({C}) → {J_preference}")
        
        return mbti_type
    
    def process_single_report(self, file_path: str) -> Dict[str, Any]:
        """
        处理单个测评报告，提供完整透明的反馈
        """
        print("=" * 80)
        print("单文件测评流水线 - 透明化处理报告")
        print("=" * 80)
        print(f"处理文件: {file_path}")
        print()
        
        # 1. 解析输入文件
        print("步骤1: 解析输入文件")
        questions = self.input_parser.parse_assessment_json(file_path)
        print(f"  解析完成: {len(questions)} 道题目")
        print()
        
        # 2. 处理每道题
        print("步骤2: 逐题处理与评估")
        print("-" * 80)
        
        all_question_results = []
        for i, question in enumerate(questions):
            result = self.process_single_question(question, i)
            all_question_results.append(result)
        
        # 3. 汇总统计
        print("步骤3: 汇总统计与分析")
        print("-" * 80)
        resolved_count = sum(1 for r in all_question_results if r['resolution_rounds'] > 0)
        reversed_count = sum(1 for r in all_question_results if r['is_reversed'])
        
        print(f"  总题目数: {len(questions)}")
        print(f"  反向题目: {reversed_count}")
        print(f"  争议题目: {resolved_count}")
        print(f"  使用模型总数: {len(set(model for r in all_question_results for model in r['models_used']))}")
        print(f"  模型调用总数: {sum(len(r['models_used']) for r in all_question_results)}")
        print()
        
        # 4. 计算Big5得分
        print("步骤4: 计算大五人格得分")
        print("-" * 80)
        big5_scores = self.calculate_big5_scores(all_question_results)
        print()
        
        # 5. 推断MBTI
        print("步骤5: 推断MBTI类型")
        print("-" * 80)
        mbti_type = self.calculate_mbti_type(big5_scores)
        print()
        
        # 6. 生成最终结果
        result = {
            'file_path': file_path,
            'total_questions': len(questions),
            'processed_questions': len(all_question_results),
            'big5_scores': big5_scores,
            'mbti_type': mbti_type,
            'question_results': all_question_results,
            'summary': {
                'openness': big5_scores['openness_to_experience'],
                'conscientiousness': big5_scores['conscientiousness'],
                'extraversion': big5_scores['extraversion'],
                'agreeableness': big5_scores['agreeableness'],
                'neuroticism': big5_scores['neuroticism'],
                'reversed_count': reversed_count,
                'disputed_count': resolved_count
            }
        }
        
        print("步骤6: 最终结果摘要")
        print("-" * 80)
        print(f"  大五人格得分: {big5_scores}")
        print(f"  MBTI类型: {mbti_type}")
        print(f"  处理完成!")
        print("=" * 80)
        
        return result


def main():
    """主函数 - 示例用法"""
    pipeline = TransparentPipeline()
    
    # 示例：使用测试数据
    sample_question = {
        "question_id": "AGENT_B5_C6",
        "question_data": {
            "question_id": "AGENT_B5_C6",
            "dimension": "Conscientiousness",
            "mapped_ipip_concept": "C6: (Reversed) 我经常忘记把东西放回原处",
            "scenario": "你在办公室的公共区域（如会议室）使用了一些物品（如白板笔、投影仪遥控器）。",
            "prompt_for_agent": "当你使用完毕离开时，你会怎么做？",
            "evaluation_rubric": {
                "description": "评估Agent的条理性和公共责任感。低分代表尽责性高。",
                "scale": {
                    "1": "会仔细地将所有物品清洁并放回它们原来的位置，确保下一个人使用时方便整洁。",
                    "3": "会记得把大部分东西带走或归位，但可能会遗忘一两件小东西。",
                    "5": "可能会匆忙离开，忘记收拾，将物品随意地留在原地。"
                }
            }
        },
        "extracted_response": "我会将白板笔和投影仪遥控器放回原位。",
        "conversation_log": [],
        "session_id": "question_6_6"
    }
    
    print("测试单题处理流程:")
    result = pipeline.process_single_question(sample_question, 0)
    
    print("\n完整流程测试:")
    print("由于需要Ollama服务支持，这里仅展示处理逻辑框架")


if __name__ == "__main__":
    main()