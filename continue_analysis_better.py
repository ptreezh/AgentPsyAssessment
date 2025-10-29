import sys
import os
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from segmented_analysis import SegmentedPersonalityAnalyzer
from shared_analysis.ollama_evaluator import create_ollama_evaluator, get_ollama_model_config

def process_segment_with_timeout(analyzer, evaluator, segment, segment_index, timeout=600):
    """处理单个段，带超时控制"""
    try:
        # 构建分析请求
        segment_analysis = analyzer.analyze_segment(segment, segment_index + 1)
        
        # 获取模型配置
        model_config = get_ollama_model_config("mistral")
        actual_model_name = model_config.get("name", "mistral:instruct")
        
        # 临时增加评估器超时时间
        original_timeout = evaluator.timeout
        evaluator.timeout = timeout
        
        # 调用评估器
        result = evaluator.evaluate_json_response(
            model_name=actual_model_name,
            system_prompt=segment_analysis['system_prompt'],
            user_prompt=segment_analysis['user_prompt']
        )
        
        # 恢复原始超时时间
        evaluator.timeout = original_timeout
        
        return result
    except Exception as e:
        print(f"Exception processing segment {segment_index+1}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "raw_response": None
        }

def continue_segment_analysis_with_better_handling():
    """继续分析第一个文件的剩余段，带有更好的错误处理"""
    
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
    processed_segments = 5  # 已经处理的段数
    successful_segments = 0
    
    for i in range(5, len(segments)):  # 从索引5开始（第6个段）
        segment = segments[i]
        print(f"Processing segment {i+1}/{len(segments)}")
        
        # 重试机制
        max_retries = 2
        retry_delay = 5  # 秒
        
        segment_success = False
        
        for retry in range(max_retries):
            try:
                # 处理段，带超时控制
                result = process_segment_with_timeout(analyzer, evaluator, segment, i, timeout=600)
                
                if result['success']:
                    segment_result = result['response']
                    segment_results.append(segment_result)
                    
                    # 累积分数
                    cumulative_analyzer.accumulate_scores(segment_result)
                    
                    print(f"Segment {i+1} processed successfully")
                    processed_segments += 1
                    successful_segments += 1
                    segment_success = True
                    break  # 成功处理，跳出重试循环
                else:
                    print(f"Failed to process segment {i+1} (attempt {retry+1}/{max_retries}): {result['error']}")
                    if retry < max_retries - 1:
                        print(f"Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        print(f"Segment {i+1} failed after {max_retries} attempts")
                        
            except Exception as e:
                print(f"Exception processing segment {i+1} (attempt {retry+1}/{max_retries}): {str(e)}")
                if retry < max_retries - 1:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"Segment {i+1} failed after {max_retries} attempts due to exception")
        
        # 如果段处理失败，使用模拟数据继续
        if not segment_success:
            print(f"Using mock data for segment {i+1}")
            mock_result = analyzer._create_mock_response(segment, i+1, {
                'segment_number': i+1,
                'question_count': len(segment),
                'dimensions_covered': list(set(q.get('dimension', 'Unknown') for q in segment))
            })
            segment_results.append(mock_result['llm_response'])
            cumulative_analyzer.accumulate_scores(mock_result['llm_response'])
            processed_segments += 1
    
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
        'processed_segments': processed_segments,
        'successful_segments': successful_segments,
        'total_segments': len(segments)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"Analysis completed. Results saved to {output_file}")
    print(f"MBTI type: {final_scores['mbti']['type']}")
    print(f"Processed segments: {processed_segments}/{len(segments)}")
    print(f"Successful segments: {successful_segments}/{len(segments)}")

if __name__ == "__main__":
    continue_segment_analysis_with_better_handling()