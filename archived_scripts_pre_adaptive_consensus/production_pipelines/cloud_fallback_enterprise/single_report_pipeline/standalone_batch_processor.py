#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终可运行的批量处理器模块
处理多个测评报告文件的完整系统
"""

import json
import ollama
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import time
import statistics
import re
import logging
import pickle
import os
import sys

# 导入其他模块
from context_generator import ContextGenerator
from reverse_scoring_processor import ReverseScoringProcessor
from input_parser import InputParser


class StandaloneBatchProcessor:
    """独立批量处理器 - 不需要相对导入"""
    
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
        
        # 准备7个评估器模型，确保品牌差异和尺度要求
        self.dispute_models = dispute_models or [
            'llama3:latest',      # Meta (第1轮第1个)
            'gemma3:latest',      # Google (第1轮第2个)
            'phi3:mini',          # Microsoft (第2轮第1个)
            'yi:6b',              # 01.AI (第2轮第2个)
            'qwen3:4b',           # Alibaba (第3轮第1个)
            'deepseek-r1:8b',     # DeepSeek (第3轮第2个)
            'mixtral:8x7b'        # Mistral AI (备用)
        ]
        
        self.context_generator = ContextGenerator()
        self.reverse_processor = ReverseScoringProcessor()
        self.input_parser = InputParser()
        
        # 争议解决参数
        self.max_dispute_rounds = 3      # 最大争议解决轮次
        self.dispute_threshold = 1.0     # 争议检测阈值
        self.checkpoint_interval = 5     # 检查点间隔
    
    def parse_scores_from_response(self, response: str) -> Dict[str, int]:
        """
        从模型响应中解析评分
        
        Args:
            response: 模型的完整响应字符串
            
        Returns:
            解析出的评分字典
        """
        # 默认评分
        default_scores = {
            'openness_to_experience': 3,
            'conscientiousness': 3,
            'extraversion': 3,
            'agreeableness': 3,
            'neuroticism': 3
        }
        
        if not response or not response.strip():
            print("    使用默认评分: 无响应")
            return default_scores
        
        try:
            # 尝试匹配 ```json``` 包裹的内容
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
            else:
                # 尝试匹配单独的JSON对象
                # 先查找scores部分
                scores_match = re.search(r'"scores"\s*:\s*\{([^}]*)\}', response, re.DOTALL)
                if scores_match:
                    # 提取scores部分并构建完整的JSON
                    scores_part = scores_match.group(0)
                    # 尝试补全JSON结构
                    full_response = f'{{ {scores_part} }}'
                    data = json.loads(full_response)
                else:
                    # 尝试直接解析整个响应
                    data = json.loads(response)
            
            if 'scores' in data:
                scores = data['scores']
                
                # 确保所有评分都在1,3,5范围内
                for trait, score in scores.items():
                    if isinstance(score, (int, float)):
                        if score <= 1.5:
                            scores[trait] = 1
                        elif score >= 4.5:
                            scores[trait] = 5
                        else:
                            scores[trait] = 3
                    elif score in [1, 3, 5]:
                        scores[trait] = score
                    else:
                        scores[trait] = 3  # 默认中性分
                
                print(f"    解析评分: {scores}")
                return scores
            else:
                print("    响应中未找到scores字段")
                return default_scores
                
        except json.JSONDecodeError as e:
            print(f"    JSON解析失败: {e}")
            print(f"    响应内容预览: {response[:200]}...")
            
            # 从文本中提取评分
            scores = default_scores.copy()
            for trait in scores:
                # 查找类似"trait: 3"或"trait = 5"的模式
                pattern = rf'{trait}.*?[=:]\s*([1-5])'
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    try:
                        scores[trait] = int(match.group(1))
                    except:
                        pass  # 保持默认分
            
            return scores
        except Exception as e:
            print(f"    响应解析异常: {e}")
            return default_scores
    
    def evaluate_single_question(self, context: str, model: str, question_id: str) -> Dict[str, int]:
        """
        使用单个模型评估单道题
        
        Args:
            context: 评估上下文
            model: 使用的模型
            question_id: 题目ID
            
        Returns:
            该题在各维度上的评分
        """
        print(f"    └─ 使用模型 {model} 评估 {question_id}...")
        
        try:
            response = ollama.generate(model=model, prompt=context, options={'num_predict': 1000})
            scores = self.parse_scores_from_response(response['response'])
            return scores
        except Exception as e:
            print(f"    ❌ 模型 {model} 调用失败: {e}")
            return {
                'openness_to_experience': 3,
                'conscientiousness': 3,
                'extraversion': 3,
                'agreeableness': 3,
                'neuroticism': 3
            }
    
    def detect_disputes(self, scores_list: List[Dict[str, int]], threshold: float = 1.0) -> Dict[str, List]:
        """检测评分争议（所有维度）"""
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
    
    def detect_major_dimension_disputes(self, scores_list: List[Dict[str, int]], question: Dict, threshold: float = 1.0) -> Dict[str, List]:
        """
        检测主要维度评分争议（只检查题目所属的主要维度）
        """
        question_data = question.get('question_data', {})
        primary_dimension = question_data.get('dimension', '')
        
        # 将主要维度映射到标准名称
        dimension_map = {
            'Extraversion': 'extraversion',
            'Agreeableness': 'agreeableness', 
            'Conscientiousness': 'conscientiousness',
            'Neuroticism': 'neuroticism',
            'Openness to Experience': 'openness_to_experience'
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
                disputes[standard_primary_dimension] = {
                    'scores': trait_scores,
                    'range': score_range,
                    'requires_resolution': True
                }
        
        return disputes
    
    def process_single_question(self, question: Dict, question_idx: int) -> Dict[str, Any]:
        """
        处理单个题目，提供详细反馈
        
        Args:
            question: 题目信息
            question_idx: 题目索引
            
        Returns:
            处理结果
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
        
        # 争议解决（每轮追加2个模型，最多3轮）
        current_scores = initial_scores.copy()
        resolution_round = 0
        all_models_used = [item['model'] for item in initial_scores]
        all_scores_data = all_initial_scores.copy()
        
        while disputes and resolution_round < self.max_dispute_rounds:
            print(f"  第 {resolution_round + 1} 轮争议解决:")
            
            # 每轮追加2个争议解决模型
            dispute_models_for_round = []
            for i in range(2):  # 每轮2个模型
                model_index = (resolution_round * 2 + i) % len(self.dispute_models)
                dispute_models_for_round.append(self.dispute_models[model_index])
            
            print(f"    使用追加模型: {dispute_models_for_round}")
            
            # 为每轮的2个模型进行评估
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
            
            # 重新检测争议（只检查主要维度）
            major_disputes = self.detect_major_dimension_disputes(all_scores_data, question, self.dispute_threshold)
            disputes = major_disputes
            resolution_round += 1
            
            if disputes:
                print(f"    仍存在 {len(disputes)} 个主要维度分歧: {list(disputes.keys())}")
                # 显示每个争议的详细信息
                for trait, dispute_info in disputes.items():
                    print(f"      {trait}: {dispute_info['scores']}")
            else:
                print(f"    所有主要维度分歧已解决")
        
        # 应用多数决策原则确定最终原始评分
        final_raw_scores = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            trait_scores = [scores_data[trait] for scores_data in all_scores_data if trait in scores_data]
            if trait_scores:
                # 使用中位数作为最终评分
                median_score = statistics.median(trait_scores)
                final_raw_scores[trait] = int(round(median_score))  # 确保是整数
            else:
                final_raw_scores[trait] = 3  # 默认值
        
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
        
        print(f"  最终评分: {final_adjusted_scores}")
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
            'scores_data': all_scores_data
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
                    # 非主要维度分数计算平均后乘以权重
                    primary_scores = [item['score'] for item in weighted_scores if item['is_primary']]
                    other_scores = [item['score'] for item in weighted_scores if not item['is_primary']]
                    
                    # 如果有主要维度分数
                    if primary_scores:
                        primary_avg = sum(primary_scores) / len(primary_scores)
                        # 如果有其他维度分数，也要计算平均
                        if other_scores:
                            other_avg = sum(other_scores) / len(other_scores)
                            # 加权计算
                            weighted_score = 0.7 * primary_avg + 0.3 * other_avg
                        else:
                            weighted_score = primary_avg
                    else:
                        # 如果没有主要维度分数，计算所有分数平均
                        all_scores = [item['score'] for item in weighted_scores]
                        weighted_score = sum(all_scores) / len(all_scores)
                    
                    big5_scores[dimension] = round(weighted_score, 2)
                    print(f"  {dimension}:")
                    if primary_scores:
                        print(f"    主要维度平均: {sum(primary_scores) / len(primary_scores):.2f} (n={len(primary_scores)})")
                    if other_scores:
                        print(f"    其他维度平均: {sum(other_scores) / len(other_scores):.2f} (n={len(other_scores)})")
                    print(f"    加权总分: {weighted_score:.2f}")
                else:
                    big5_scores[dimension] = 3.0  # 默认中性分
                    print(f"  {dimension}: 无评分数据，使用默认值3.0")
            else:
                big5_scores[dimension] = 3.0  # 默认中性分
                print(f"  {dimension}: 无评分数据，使用默认值3.0")
        
        return big5_scores
    
    def calculate_mbti_type(self, big5_scores: Dict[str, float]) -> str:
        """基于大五人格得分推断MBTI类型"""
        print("推断MBTI类型:")
        
        # 简化的MBTI推断逻辑
        O = big5_scores.get('openness_to_experience', 3)
        C = big5_scores.get('conscientiousness', 3)
        E = big5_scores.get('extraversion', 3)
        A = big5_scores.get('agreeableness', 3)
        N = big5_scores.get('neuroticism', 3)
        
        # E/I维度：外向性 vs 内向性（包含神经质因素）
        e_score = E + (5 - N)  # 高外向性+低神经质=外向
        i_score = (5 - E) + N  # 高神经质+低外向性=内向
        E_preference = 'E' if e_score > i_score else 'I'
        
        # S/N维度：开放性（通常开放性高=直觉N，开放性低=感觉S）
        S_preference = 'S' if O <= 3 else 'N'
        
        # T/F维度：宜人性（宜人性高=F，宜人性低=T）
        T_preference = 'T' if A <= 3 else 'F'
        
        # J/P维度：尽责性（尽责性高=判断J，尽责性低=知觉P）
        J_preference = 'J' if C > 3 else 'P'
        
        mbti_type = f"{E_preference}{S_preference}{T_preference}{J_preference}"
        
        print(f"  E/I: E({E}) vs I({5-E}) + N({N}) → {E_preference}")
        print(f"  S/N: O({O}) → {S_preference}")
        print(f"  T/F: A({A}) → {T_preference}") 
        print(f"  J/P: C({C}) → {J_preference}")
        print(f"  MBTI类型: {mbti_type}")
        
        return mbti_type
    
    def process_single_report(self, file_path: str) -> Dict[str, Any]:
        """
        处理单个测评报告
        
        Args:
            file_path: 测评报告文件路径
            
        Returns:
            处理结果
        """
        print(f"处理测评报告: {file_path}")
        print("-" * 80)
        
        start_time = time.time()
        
        try:
            # 解析输入文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assessment_results = data.get('assessment_results', [])
            
            if not assessment_results:
                print(f"❌ 未找到assessment_results字段")
                return None
            
            print(f"找到 {len(assessment_results)} 道题目")
            
            # 处理每道题
            question_results = []
            for i, question in enumerate(assessment_results):
                result = self.process_single_question(question, i)
                question_results.append(result)
                
                # 显示进度
                if (i + 1) % 10 == 0:
                    print(f"📊 进度: {i + 1}/{len(assessment_results)} 题已处理")
            
            # 计算大五人格得分
            print(f"开始计算大五人格得分...")
            big5_scores = self.calculate_big5_scores(question_results)
            
            # 推断MBTI类型
            mbti_type = self.calculate_mbti_type(big5_scores)
            
            # 计算总体统计数据
            total_time = time.time() - start_time
            reversed_count = sum(1 for r in question_results if r['is_reversed'])
            disputed_count = sum(1 for r in question_results if r['resolution_rounds'] > 0)
            models_called = sum(len(r['models_used']) for r in question_results)
            
            result = {
                'success': True,
                'file_path': file_path,
                'processing_time': round(total_time, 1),
                'big5_scores': big5_scores,
                'mbti_type': mbti_type,
                'question_results': question_results,
                'summary': {
                    'total_questions': len(assessment_results),
                    'reversed_count': reversed_count,
                    'disputed_count': disputed_count,
                    'models_called': models_called,
                    'average_time_per_question': round(total_time / len(assessment_results), 1) if assessment_results else 0
                }
            }
            
            print(f"\n处理完成!")
            print(f"总时间: {total_time:.1f} 秒")
            print(f"大五人格得分: {big5_scores}")
            print(f"MBTI类型: {mbti_type}")
            print(f"反向题目数: {reversed_count}")
            print(f"争议解决数: {disputed_count}")
            
            return result
            
        except Exception as e:
            print(f"❌ 处理文件 {file_path} 失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }


def main():
    """主函数 - 演示用法"""
    print("独立批量处理器 - 演示模式")
    print("="*60)
    
    # 创建处理器实例
    processor = StandaloneBatchProcessor()
    
    # 示例文件路径
    sample_file = r"..\results\readonly-original\asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    
    if os.path.exists(sample_file):
        print(f"找到示例文件: {sample_file}")
        
        # 处理单个文件
        result = processor.process_single_report(sample_file)
        
        if result and result.get('success', False):
            print(f"\n✅ 文件处理成功!")
            print(f"大五人格得分: {result['big5_scores']}")
            print(f"MBTI类型: {result['mbti_type']}")
            print(f"处理时间: {result['processing_time']:.1f}秒")
        else:
            print(f"\n❌ 文件处理失败!")
            error_msg = result.get('error', 'Unknown error') if result else 'No result'
            print(f"错误: {error_msg}")
    else:
        print(f"❌ 示例文件不存在: {sample_file}")
        print("请确保在正确的目录结构下运行此脚本")


if __name__ == "__main__":
    main()