#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的多评估器系统
优先使用三个核心评估器，仅在需要时增加更多评估器
"""

import argparse
import json
import sys
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from enhanced_cloud_analyzer import EnhancedCloudAnalyzer

class OptimizedMultiEvaluator:
    """优化的多评估器系统"""

    def __init__(self, api_key: str = None):
        # 核心评估器（优先使用）
        self.core_evaluators = ["ollama_mistral", "phi3_mini", "qwen3_4b"]
        
        # 备用评估器（仅在核心评估器失败或不一致时使用）
        self.backup_evaluators = ["qwen-long", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        
        self.api_key = api_key
        self.results = {}
        self.consensus_threshold = 0.7  # 一致性阈值

    def evaluate_with_core_models(self, input_file: Path, output_dir: Path) -> Dict:
        """使用核心评估器进行优先评估"""
        print("🎯 开始核心评估器分析")
        print(f"📊 核心评估器: {', '.join(self.core_evaluators)}")

        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        core_results = {}
        
        # 首先尝试所有核心评估器
        for model in self.core_evaluators:
            print(f"\n🔍 正在使用核心评估器 {model}...")
            
            result = self._evaluate_with_single_model(model, input_file, output_dir)
            core_results[model] = result
            
            if result['success']:
                big5_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in result['big5_scores'].items()])
                print(f"✅ {model} - Big5: {big5_str} - MBTI: {result['mbti_type']}")
            else:
                print(f"❌ {model} 评估失败: {result.get('error', 'Unknown error')}")

        # 检查核心评估器的一致性
        consensus_analysis = self._check_core_consensus(core_results)
        
        if consensus_analysis['consensus_achieved']:
            print(f"🎉 核心评估器达成共识 (一致性: {consensus_analysis['consensus_score']:.2f})")
            return {
                'success': True,
                'results': core_results,
                'consensus_analysis': consensus_analysis,
                'evaluators_used': self.core_evaluators,
                'backup_used': False
            }
        else:
            print(f"⚠️ 核心评估器未达成共识 (一致性: {consensus_analysis['consensus_score']:.2f})")
            print("🔄 启用备用评估器...")
            return self._evaluate_with_backup_models(input_file, output_dir, core_results)

    def _evaluate_with_single_model(self, model: str, input_file: Path, output_dir: Path) -> Dict:
        """使用单个模型进行评估"""
        try:
            analyzer = EnhancedCloudAnalyzer(
                model=model,
                api_key=self.api_key
            )

            if not analyzer.api_available:
                return {
                    'success': False,
                    'error': 'API不可用'
                }

            # 为每个模型创建独立目录
            model_dir = output_dir / model
            model_dir.mkdir(exist_ok=True)

            # 执行分析
            result = analyzer.analyze_full_assessment(str(input_file), str(model_dir))

            if result['success']:
                final_scores = result.get('final_scores', {})
                mbti_result = result.get('mbti_result', {})
                
                return {
                    'success': True,
                    'big5_scores': {trait: data.get('final_score', 3) for trait, data in final_scores.items()},
                    'mbti_type': mbti_result.get('type', 'Unknown'),
                    'final_scores_detailed': final_scores,
                    'mbti_detailed': mbti_result,
                    'summary_file': result.get('summary_file', 'N/A'),
                    'evidence_file': result.get('evidence_file', 'N/A')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_core_consensus(self, core_results: Dict) -> Dict:
        """检查核心评估器之间的一致性"""
        successful_results = {k: v for k, v in core_results.items() if v['success']}
        
        if len(successful_results) < 2:
            return {
                'consensus_achieved': False,
                'consensus_score': 0.0,
                'successful_count': len(successful_results),
                'total_count': len(self.core_evaluators)
            }

        # 计算Big5分数的一致性
        big5_consensus_scores = []
        models = list(successful_results.keys())
        
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                model1, model2 = models[i], models[j]
                scores1 = successful_results[model1]['big5_scores']
                scores2 = successful_results[model2]['big5_scores']
                
                # 计算两个模型间的一致性分数
                consensus = self._calculate_pair_consensus(scores1, scores2)
                big5_consensus_scores.append(consensus)

        # 计算MBTI类型的一致性
        mbti_types = [result['mbti_type'] for result in successful_results.values()]
        mbti_consensus = len(set(mbti_types)) == 1  # 所有类型是否相同
        
        overall_consensus = sum(big5_consensus_scores) / len(big5_consensus_scores) if big5_consensus_scores else 0
        
        return {
            'consensus_achieved': overall_consensus >= self.consensus_threshold and mbti_consensus,
            'consensus_score': overall_consensus,
            'mbti_consensus': mbti_consensus,
            'successful_count': len(successful_results),
            'total_count': len(self.core_evaluators),
            'big5_consensus_scores': big5_consensus_scores
        }

    def _calculate_pair_consensus(self, scores1: Dict, scores2: Dict) -> float:
        """计算两个模型对的一致性分数"""
        if not scores1 or not scores2:
            return 0.0
            
        differences = []
        for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            if trait in scores1 and trait in scores2:
                diff = abs(scores1[trait] - scores2[trait])
                differences.append(diff)
        
        if not differences:
            return 0.0
            
        # 转换为一致性分数（差异越小，一致性越高）
        avg_diff = sum(differences) / len(differences)
        consensus = max(0, 1 - (avg_diff / 5))  # 假设5分制，最大差异为5
        
        return consensus

    def _evaluate_with_backup_models(self, input_file: Path, output_dir: Path, core_results: Dict) -> Dict:
        """使用备用评估器进行补充评估"""
        print(f"🔄 启用备用评估器: {', '.join(self.backup_evaluators)}")
        
        all_results = core_results.copy()
        
        # 尝试备用评估器
        for model in self.backup_evaluators:
            print(f"\n🔍 正在使用备用评估器 {model}...")
            
            result = self._evaluate_with_single_model(model, input_file, output_dir)
            all_results[model] = result
            
            if result['success']:
                big5_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in result['big5_scores'].items()])
                print(f"✅ {model} - Big5: {big5_str} - MBTI: {result['mbti_type']}")
            else:
                print(f"❌ {model} 评估失败: {result.get('error', 'Unknown error')}")

        # 重新计算所有评估器的一致性
        final_consensus = self._check_final_consensus(all_results)
        
        successful_evaluators = [model for model, result in all_results.items() if result['success']]
        
        return {
            'success': len(successful_evaluators) > 0,
            'results': all_results,
            'consensus_analysis': final_consensus,
            'evaluators_used': self.core_evaluators + self.backup_evaluators,
            'backup_used': True,
            'successful_evaluators': successful_evaluators
        }

    def _check_final_consensus(self, all_results: Dict) -> Dict:
        """检查所有评估器的最终一致性"""
        successful_results = {k: v for k, v in all_results.items() if v['success']}
        
        if len(successful_results) < 2:
            return {
                'consensus_achieved': False,
                'consensus_score': 0.0,
                'successful_count': len(successful_results),
                'total_count': len(all_results)
            }

        # 计算多数投票
        big5_scores_by_trait = {}
        mbti_types = []
        
        for result in successful_results.values():
            mbti_types.append(result['mbti_type'])
            for trait, score in result['big5_scores'].items():
                if trait not in big5_scores_by_trait:
                    big5_scores_by_trait[trait] = []
                big5_scores_by_trait[trait].append(score)

        # 计算共识分数
        consensus_scores = []
        for trait_scores in big5_scores_by_trait.values():
            if len(trait_scores) > 1:
                avg_score = sum(trait_scores) / len(trait_scores)
                variance = sum((score - avg_score) ** 2 for score in trait_scores) / len(trait_scores)
                consensus = max(0, 1 - (variance / 4))  # 假设方差最大为4
                consensus_scores.append(consensus)

        overall_consensus = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0
        
        # MBTI多数投票
        from collections import Counter
        mbti_counter = Counter(mbti_types)
        most_common_mbti, mbti_count = mbti_counter.most_common(1)[0]
        mbti_consensus = mbti_count / len(mbti_types)
        
        return {
            'consensus_achieved': overall_consensus >= self.consensus_threshold and mbti_consensus >= 0.5,
            'consensus_score': overall_consensus,
            'mbti_consensus': mbti_consensus >= 0.5,
            'mbti_majority': most_common_mbti,
            'mbti_confidence': mbti_consensus,
            'successful_count': len(successful_results),
            'total_count': len(all_results)
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='优化的多评估器系统')
    parser.add_argument('input_file', help='输入测评文件路径')
    parser.add_argument('--output_dir', default='./optimized_evaluation_results', help='输出目录')
    parser.add_argument('--api_key', help='API密钥')
    
    args = parser.parse_args()
    
    evaluator = OptimizedMultiEvaluator(api_key=args.api_key)
    
    result = evaluator.evaluate_with_core_models(
        Path(args.input_file), 
        Path(args.output_dir)
    )
    
    print(f"\n🎯 最终结果:")
    print(f"成功: {'是' if result['success'] else '否'}")
    print(f"使用的评估器: {len(result['evaluators_used'])} 个")
    print(f"是否使用备用评估器: {'是' if result.get('backup_used', False) else '否'}")
    print(f"一致性分数: {result['consensus_analysis']['consensus_score']:.3f}")
    print(f"是否达成共识: {'是' if result['consensus_analysis']['consensus_achieved'] else '否'}")

if __name__ == '__main__':
    main()