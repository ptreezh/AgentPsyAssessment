#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单文件评估流水线主模块
整合上下文生成、多模型评估、反向计分处理和Big5计算
"""

import json
import ollama
from typing import Dict, List, Any
from .context_generator import ContextGenerator
from .reverse_scoring_processor import ReverseScoringProcessor
from .input_parser import InputParser
import time
import statistics


class SingleReportPipeline:
    """单文件评估流水线"""
    
    def __init__(self, primary_models: List[str] = None, dispute_models: List[str] = None):
        """
        初始化流水线
        
        Args:
            primary_models: 主要评估模型列表（默认3个不同品牌）
            dispute_models: 争议解决模型列表（用于追加评估）
        """
        self.primary_models = primary_models or [
            'qwen3:8b',
            'deepseek-r1:8b', 
            'mistral-nemo:latest'
        ]
        
        self.dispute_models = dispute_models or [
            'llama3:latest',
            'gemma3:latest'
        ]
        
        self.context_generator = ContextGenerator()
        self.reverse_processor = ReverseScoringProcessor()
        self.input_parser = InputParser()
        self.max_dispute_rounds = 3
        self.dispute_threshold = 1.0  # 分数差异阈值
    
    def parse_scores_from_response(self, response: str) -> Dict[str, int]:
        """
        从模型响应中解析评分
        
        Args:
            response: 模型的完整响应
            
        Returns:
            解析出的评分字典
        """
        import re
        import json
        
        # 尝试查找JSON部分
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group()
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
    
    def evaluate_single_question(self, context: str, model: str) -> Dict[str, int]:
        """
        使用单个模型评估单道题
        
        Args:
            context: 评估上下文
            model: 评估模型
            
        Returns:
            该模型的评分结果
        """
        try:
            response = ollama.generate(model=model, prompt=context, options={'num_predict': 2000})
            scores = self.parse_scores_from_response(response['response'])
            return scores
        except Exception as e:
            print(f"模型 {model} 评估失败: {e}")
            # 返回默认评分
            return {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
    
    def evaluate_with_multiple_models(self, context: str, models: List[str]) -> List[Dict[str, int]]:
        """
        使用多个模型评估单道题
        
        Args:
            context: 评估上下文
            models: 模型列表
            
        Returns:
            各模型的评分结果列表
        """
        all_scores = []
        for model in models:
            print(f"  使用模型 {model} 评估...")
            scores = self.evaluate_single_question(context, model)
            all_scores.append(scores)
            time.sleep(1)  # 防止API过载
        return all_scores
    
    def detect_disputes(self, scores_list: List[Dict[str, int]], threshold: float = 1.0) -> Dict[str, List]:
        """
        检测评分争议
        
        Args:
            scores_list: 多个模型的评分列表
            threshold: 分歧阈值
            
        Returns:
            分歧详情字典
        """
        disputes = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            trait_scores = [scores[trait] for scores in scores_list if trait in scores]
            if len(trait_scores) > 1:
                score_range = max(trait_scores) - min(trait_scores)
                if score_range > threshold:
                    disputes[trait] = {
                        'scores': trait_scores,
                        'range': score_range,
                        'requires_resolution': True
                    }
        
        return disputes
    
    def resolve_disputes(self, question_info: Dict, disputes: Dict[str, List], 
                        all_scores: List[Dict[str, int]]) -> List[Dict[str, int]]:
        """
        解决评分争议
        
        Args:
            question_info: 题目信息
            disputes: 分歧详情
            all_scores: 当前所有评分
            
        Returns:
            包含追加评估的更新后评分列表
        """
        if not disputes:
            return all_scores
        
        print(f"  发现分歧，使用追加模型进行重新评估...")
        
        # 生成新的评估上下文
        context = self.context_generator.generate_evaluation_prompt(question_info)
        
        # 使用争议解决模型进行额外评估
        additional_scores = self.evaluate_with_multiple_models(context, self.dispute_models[:2])
        
        # 合并所有评分
        updated_scores = all_scores + additional_scores
        
        return updated_scores
    
    def apply_majority_decision(self, scores_list: List[Dict[str, int]]) -> Dict[str, int]:
        """
        应用多数决策原则确定最终评分
        
        Args:
            scores_list: 所有评估的评分列表
            
        Returns:
            最终评分
        """
        final_scores = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            trait_scores = [scores[trait] for scores in scores_list if trait in scores]
            if trait_scores:
                # 使用中位数作为最终评分
                final_scores[trait] = int(statistics.median(trait_scores))
            else:
                final_scores[trait] = 3  # 默认值
        
        return final_scores
    
    def process_single_report(self, file_path: str) -> Dict[str, Any]:
        """
        处理单个测评报告
        
        Args:
            file_path: 测评报告文件路径
            
        Returns:
            包含Big5评分的完整结果
        """
        print(f"开始处理测评报告: {file_path}")
        
        # 1. 解析输入文件
        print("1. 解析输入文件...")
        questions = self.input_parser.parse_assessment_json(file_path)
        print(f"   解析完成，共 {len(questions)} 道题")
        
        # 2. 初始化结果收集器
        all_question_results = []
        
        # 3. 对每道题进行多模型评估和争议解决
        for i, question in enumerate(questions):
            print(f"2.{i+1:02d}. 处理第 {i+1} 题 (ID: {question['question_id']})...")
            
            # 生成评估上下文
            context = self.context_generator.generate_evaluation_prompt(question)
            
            # 进行初始评估（使用3个主要模型）
            print(f"     初始评估...")
            initial_scores = self.evaluate_with_multiple_models(context, self.primary_models)
            
            # 检查是否存在争议
            disputes = self.detect_disputes(initial_scores, self.dispute_threshold)
            
            # 如果存在争议，进行争议解决
            current_scores = initial_scores
            resolution_round = 0
            
            while disputes and resolution_round < self.max_dispute_rounds:
                print(f"     第 {resolution_round + 1} 轮争议解决...")
                current_scores = self.resolve_disputes(question, disputes, current_scores)
                
                # 重新检测争议
                disputes = self.detect_disputes(current_scores, self.dispute_threshold)
                resolution_round += 1
                
                if disputes:
                    print(f"     仍有 {len(disputes)} 个维度存在分歧")
            
            # 应用多数决策原则确定最终评分
            final_scores = self.apply_majority_decision(current_scores)
            
            # 记录结果
            question_result = {
                'question_id': question['question_id'],
                'question_info': question,
                'initial_scores': initial_scores,
                'final_scores': final_scores,
                'resolution_rounds': resolution_round,
                'disputes_resolved': bool(disputes),  # 是否有争议未完全解决
                'scores_count': len(current_scores)
            }
            
            all_question_results.append(question_result)
            
            print(f"     完成，最终评分: {final_scores}")
        
        # 4. 处理反向计分
        print("3. 处理反向计分...")
        processed_results = self.reverse_processor.process_scores_for_big5_calculation(
            [{'question_id': r['question_id'], 'question_info': r['question_info'], 'scores': r['final_scores']} 
             for r in all_question_results]
        )
        
        # 5. 计算Big5总分
        print("4. 计算大五人格得分...")
        big5_scores = self.reverse_processor.calculate_big5_scores(processed_results)
        
        # 6. 生成最终结果
        result = {
            'file_path': file_path,
            'total_questions': len(questions),
            'processed_questions': len(all_question_results),
            'big5_scores': big5_scores,
            'question_results': all_question_results,
            'processed_scores': processed_results,
            'summary': {
                'openness': big5_scores['openness_to_experience'],
                'conscientiousness': big5_scores['conscientiousness'],
                'extraversion': big5_scores['extraversion'],
                'agreeableness': big5_scores['agreeableness'],
                'neuroticism': big5_scores['neuroticism']
            }
        }
        
        print("5. 处理完成！")
        print(f"   大五人格得分: {big5_scores}")
        
        return result


def main():
    """主函数 - 示例用法"""
    # 实例化流水线
    pipeline = SingleReportPipeline()
    
    # 示例：处理一个测评报告
    sample_file = r"D:\AIDevelop\portable_psyagent\results\readonly-original\asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    
    print("单文件评估流水线测试")
    print("="*60)
    
    try:
        # 处理测评报告
        result = pipeline.process_single_report(sample_file)
        
        print("\n" + "="*60)
        print("最终结果摘要:")
        print(f"文件: {result['file_path']}")
        print(f"总题数: {result['total_questions']}")
        print(f"大五人格得分: {result['summary']}")
        
        # 统计争议解决情况
        resolved_count = sum(1 for r in result['question_results'] if r['resolution_rounds'] > 0)
        print(f"需要争议解决的题目数: {resolved_count}")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()