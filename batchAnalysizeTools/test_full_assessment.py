#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整50题评估
"""

import json
import sys
import os
import io

# 确保在Windows上使用UTF-8编码
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加batchAnalysizeTools目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'batchAnalysizeTools'))

from batch_segmented_analysis import BatchSegmentedPersonalityAnalyzer

def test_full_assessment():
    """测试完整50题评估"""
    print("加载完整评估文件...")
    try:
        with open("../results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json", 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        print("文件加载成功")
    except Exception as e:
        print(f"文件加载失败: {e}")
        return
    
    print("初始化分析器...")
    try:
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=2,  # 每段2个问题
            evaluator_name="gemma3",
            base_url="http://localhost:11434"
        )
        print("分析器初始化成功")
    except Exception as e:
        print(f"分析器初始化失败: {e}")
        return
    
    print("提取问题...")
    try:
        questions = analyzer.extract_questions(assessment_data)
        print(f"成功提取 {len(questions)} 个问题")
    except Exception as e:
        print(f"问题提取失败: {e}")
        return
    
    print("创建分段...")
    try:
        segments = analyzer.create_segments(questions)
        print(f"成功创建 {len(segments)} 个分段")
    except Exception as e:
        print(f"分段创建失败: {e}")
        return
    
    # 为了节省时间，我们只测试前几个分段
    test_segments = segments[:3]  # 只测试前3个分段(6个问题)
    print(f"开始分析前 {len(test_segments)} 个分段 ({len(test_segments)*2} 个问题)...")
    
    for i, segment in enumerate(test_segments):
        print(f"分析第 {i+1} 个分段...")
        try:
            segment_analysis = analyzer.analyze_segment(segment, i+1)
            if 'llm_response' in segment_analysis:
                analyzer.accumulate_scores(segment_analysis['llm_response'])
                print(f"  分段 {i+1} 分析完成")
            else:
                print(f"  分段 {i+1} 分析失败")
        except Exception as e:
            print(f"  分段 {i+1} 分析出错: {e}")
            continue
    
    print("计算最终分数...")
    try:
        final_scores = analyzer.calculate_final_scores()
        print("最终分数计算成功")
        
        # 显示Big Five分数
        print("\nBig Five 分数:")
        for trait, data in final_scores['big_five'].items():
            print(f"  {trait}: {data['score']}/10.0 (基于 {data['weight']} 个问题)")
        
        # 显示MBTI和Belbin
        print(f"\nMBTI 类型: {final_scores['mbti']['type']} (置信度: {final_scores['mbti']['confidence']})")
        print(f"Belbin 角色: 主要角色 {final_scores['belbin']['primary_role']}, 次要角色 {final_scores['belbin']['secondary_role']}")
        
        # 显示问题级别评分数量
        print(f"\n问题级别评分数量: {len(final_scores['per_question_scores'])}")
        
    except Exception as e:
        print(f"最终分数计算失败: {e}")
        return
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_full_assessment()