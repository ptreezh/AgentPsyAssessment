#!/usr/bin/env python3
"""
快速多评估器测试 - 使用2个评估器分析1个文件
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        from shared_analysis.ollama_evaluator import get_ollama_evaluators, create_ollama_evaluator
        from segmented_analysis import SegmentedPersonalityAnalyzer
        
        print("=== 快速多评估器测试 ===\n")
        
        # 只使用2个最快的评估器
        fast_evaluators = {
            'phi3_mini': 'phi3_mini',  # 本地轻量模型
            'ollama_mistral': 'mistral'  # 本地推理模型
        }
        
        print(f"使用的评估器: {list(fast_evaluators.keys())}")
        
        # 选择第一个测评文件
        input_dir = Path("results/results")
        raw_files = list(input_dir.glob("*.json"))
        
        if not raw_files:
            print("没有找到测评报告文件")
            return
            
        test_file = raw_files[0]
        print(f"测试文件: {test_file.name}")
        
        # 加载测试数据
        with open(test_file, 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        
        # 创建分段分析器
        analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=5)
        
        # 提取问题
        questions = analyzer.extract_questions(assessment_data)
        print(f"问题数量: {len(questions)}")
        
        # 创建分段
        segments = analyzer.create_segments(questions)
        print(f"分段数量: {len(segments)}")
        
        # 使用2个评估器并行分析
        evaluator_results = {}
        
        for evaluator_name, model_key in fast_evaluators.items():
            print(f"\n=== 使用 {evaluator_name} 分析 ===")
            
            try:
                # 创建评估器
                evaluator = create_ollama_evaluator(evaluator_name)
                if not evaluator:
                    print(f"  无法创建评估器: {evaluator_name}")
                    continue
                
                # 为每个评估器创建新的分析器实例
                evaluator_analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=5)
                evaluator_analyzer.evaluator = evaluator
                evaluator_analyzer.evaluator_name = evaluator_name
                
                segment_results = []
                
                # 分析每个分段
                for i, segment in enumerate(segments[:3]):  # 只分析前3个分段以加快速度
                    print(f"  分析段 {i+1}/{len(segments[:3])}")
                    
                    segment_analysis = evaluator_analyzer.analyze_segment(segment, i+1)
                    
                    if 'llm_response' in segment_analysis:
                        evaluator_analyzer.accumulate_scores(segment_analysis['llm_response'])
                        segment_results.append(segment_analysis['llm_response'])
                        print(f"    段 {i+1} 分析成功")
                    else:
                        print(f"    段 {i+1} 分析失败")
                        break
                
                # 计算最终分数
                final_scores = evaluator_analyzer.calculate_final_scores()
                
                evaluator_results[evaluator_name] = {
                    'segment_count': len(segments[:3]),
                    'question_count': len(questions),
                    'segment_results': segment_results,
                    'final_scores': final_scores
                }
                
                print(f"  ✓ {evaluator_name} 分析完成")
                print(f"  MBTI类型: {final_scores['mbti']['type']} (置信度: {final_scores['mbti']['confidence']})")
                
            except Exception as e:
                print(f"  ✗ {evaluator_name} 分析失败: {e}")
        
        # 对比评估器结果
        if evaluator_results:
            print(f"\n=== 评估器对比结果 ===")
            
            # MBTI类型对比
            mbti_types = {}
            for eval_name, result in evaluator_results.items():
                mbti = result['final_scores'].get('mbti', {})
                mbti_type = mbti.get('type', 'Unknown')
                confidence = mbti.get('confidence', 0)
                mbti_types[eval_name] = mbti_type
                print(f"{eval_name}: {mbti_type} (置信度: {confidence:.2f})")
            
            # 计算MBTI一致性
            unique_types = set(mbti_types.values())
            if len(unique_types) == 1:
                print(f"✓ MBTI类型完全一致: {list(unique_types)[0]}")
            else:
                print(f"⚠ MBTI类型不一致: {mbti_types}")
            
            # Big Five分数对比
            print(f"\nBig Five分数对比:")
            traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
            
            for trait in traits:
                scores = []
                for eval_name, result in evaluator_results.items():
                    big_five = result['final_scores'].get('big_five', {})
                    trait_data = big_five.get(trait, {})
                    score = trait_data.get('score', 5.0)
                    scores.append(score)
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    max_score = max(scores)
                    min_score = min(scores)
                    variation = max_score - min_score
                    
                    print(f"  {trait}: 平均={avg_score:.1f}, 范围={min_score:.1f}-{max_score:.1f}, 变异度={variation:.1f}")
        
        print(f"\n=== 测试完成 ===")
        print(f"成功评估器: {len(evaluator_results)}/{len(fast_evaluators)}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()