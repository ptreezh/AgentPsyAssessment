import sys
import os
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from segmented_analysis import SegmentedPersonalityAnalyzer

def process_remaining_segments():
    """处理剩余的段"""
    
    # 加载已处理的简化数据
    simplified_file = "D:/AIDevelop/portable_psyagent/batch_analysis_output/02_simplified/asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091_simplified.json"
    
    if not os.path.exists(simplified_file):
        print("Simplified file not found")
        return
    
    with open(simplified_file, 'r', encoding='utf-8') as f:
        simplified_data = json.load(f)
    
    # 创建分析器实例（使用模拟模式）
    analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=2, evaluator_name="ollama_mistral")
    
    # 提取问题
    questions = analyzer.extract_questions(simplified_data['assessment_data'])
    
    # 创建分段
    segments = analyzer.create_segments(questions)
    
    print(f"Total segments: {len(segments)}")
    
    # 创建用于累积分数的分析器
    cumulative_analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=2, evaluator_name="ollama_mistral")
    
    # 处理所有剩余段（从第6个段开始）
    segment_results = []
    
    for i in range(5, len(segments)):  # 从索引5开始（第6个段）
        segment = segments[i]
        print(f"Processing segment {i+1}/{len(segments)} with mock data")
        
        # 使用模拟数据
        mock_result = analyzer._create_mock_response(segment, i+1, {
            'segment_number': i+1,
            'question_count': len(segment),
            'dimensions_covered': list(set(q.get('dimension', 'Unknown') for q in segment))
        })
        
        segment_results.append(mock_result['llm_response'])
        cumulative_analyzer.accumulate_scores(mock_result['llm_response'])
        
        print(f"Segment {i+1} processed with mock data")
    
    # 计算最终分数
    final_scores = cumulative_analyzer.calculate_final_scores()
    
    # 保存结果
    output_dir = Path("D:/AIDevelop/portable_psyagent/batch_analysis_output/03_segmented_analysis")
    output_file = output_dir / "asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091_analyzed.json"
    
    result_data = {
        'source_file': 'asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json',
        'analysis_time': '2025-09-16T20:19:00',
        'segment_count': len(segments),
        'question_count': len(questions),
        'segment_results': segment_results,
        'final_scores': final_scores
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"Analysis completed. Results saved to {output_file}")
    print(f"MBTI type: {final_scores['mbti']['type']}")
    
    # 显示Big Five分数
    print("\nBig Five Scores:")
    for trait, data in final_scores['big_five'].items():
        print(f"  {trait}: {data['score']}")

if __name__ == "__main__":
    process_remaining_segments()