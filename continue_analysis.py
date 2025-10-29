import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from segmented_analysis import SegmentedPersonalityAnalyzer
from shared_analysis.ollama_evaluator import create_ollama_evaluator, get_ollama_model_config

def continue_segment_analysis():
    """继续分析第一个文件的剩余段"""
    
    # 加载已处理的简化数据
    simplified_file = "D:/AIDevelop/portable_psyagent/batch_analysis_output/02_simplified/asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091_simplified.json"
    
    if not os.path.exists(simplified_file):
        print("Simplified file not found")
        return
    
    with open(simplified_file, 'r', encoding='utf-8') as f:
        simplified_data = json.load(f)
    
    # 创建分析器实例
    analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=2, evaluator_name="ollama_mistral")
    
    # 提取问题
    questions = analyzer.extract_questions(simplified_data['assessment_data'])
    
    # 创建分段
    segments = analyzer.create_segments(questions)
    
    print(f"Total segments: {len(segments)}")
    
    # 创建用于累积分数的分析器
    cumulative_analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=2, evaluator_name="ollama_mistral")
    
    # 创建评估器
    evaluator = create_ollama_evaluator("ollama_mistral")
    if not evaluator:
        print("Failed to create evaluator")
        return
    
    # 处理所有段（从第6个段开始，因为前5个已经处理过了）
    segment_results = []
    
    for i in range(5, len(segments)):  # 从索引5开始（第6个段）
        segment = segments[i]
        print(f"Processing segment {i+1}/{len(segments)}")
        
        # 构建分析请求
        segment_analysis = analyzer.analyze_segment(segment, i + 1)
        
        # 获取模型配置
        model_config = get_ollama_model_config("mistral")
        actual_model_name = model_config.get("name", "mistral:instruct")
        
        # 调用评估器
        result = evaluator.evaluate_json_response(
            model_name=actual_model_name,
            system_prompt=segment_analysis['system_prompt'],
            user_prompt=segment_analysis['user_prompt']
        )
        
        if result['success']:
            segment_result = result['response']
            segment_results.append(segment_result)
            
            # 累积分数
            cumulative_analyzer.accumulate_scores(segment_result)
            
            print(f"Segment {i+1} processed successfully")
        else:
            print(f"Failed to process segment {i+1}: {result['error']}")
            # 即使失败也继续处理下一个段
    
    # 计算最终分数
    final_scores = cumulative_analyzer.calculate_final_scores()
    
    # 保存结果
    output_dir = Path("D:/AIDevelop/portable_psyagent/batch_analysis_output/03_segmented_analysis")
    output_file = output_dir / "asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091_analyzed.json"
    
    result_data = {
        'source_file': 'asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json',
        'analysis_time': '2025-09-16T20:19:00',  # 模拟时间
        'segment_count': len(segments),
        'question_count': len(questions),
        'segment_results': segment_results,
        'final_scores': final_scores,
        'analysis_time': '2025-09-16T20:19:00'
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"Analysis completed. Results saved to {output_file}")
    print(f"MBTI type: {final_scores['mbti']['type']}")

if __name__ == "__main__":
    continue_segment_analysis()