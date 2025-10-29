#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成完整50题测评报告
"""

import json
import sys
import os

# 添加batchAnalysizeTools目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'batchAnalysizeTools'))

from batch_segmented_analysis import BatchSegmentedPersonalityAnalyzer

def generate_full_assessment_report():
    """生成完整的50题测评报告"""
    print("Loading assessment file...")
    try:
        with open("results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json", 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        print("File loaded successfully")
    except Exception as e:
        print(f"Failed to load file: {e}")
        return
    
    print("Initializing analyzer...")
    try:
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=2,  # 2 questions per segment
            evaluator_name="gemma3",
            base_url="http://localhost:11434"
        )
        print("Analyzer initialized successfully")
    except Exception as e:
        print(f"Failed to initialize analyzer: {e}")
        return
    
    print("Extracting questions...")
    try:
        questions = analyzer.extract_questions(assessment_data)
        print(f"Successfully extracted {len(questions)} questions")
    except Exception as e:
        print(f"Failed to extract questions: {e}")
        return
    
    print("Creating segments...")
    try:
        segments = analyzer.create_segments(questions)
        print(f"Successfully created {len(segments)} segments")
    except Exception as e:
        print(f"Failed to create segments: {e}")
        return
    
    print(f"Analyzing all {len(segments)} segments ({len(questions)} questions)...\n")
    
    # Analyze all segments
    successful_segments = 0
    for i, segment in enumerate(segments):
        print(f"Analyzing segment {i+1} ({len(segment)} questions)...\n")
        try:
            segment_analysis = analyzer.analyze_segment(segment, i+1)
            if 'llm_response' in segment_analysis:
                analyzer.accumulate_scores(segment_analysis['llm_response'])
                successful_segments += 1
                print(f"  Segment {i+1} analyzed successfully\n")
            else:
                print(f"  Segment {i+1} analysis failed\n")
        except Exception as e:
            print(f"  Segment {i+1} analysis error: {e}\n")
            continue
    
    print(f"Successfully analyzed {successful_segments}/{len(segments)} segments\n")
    
    print("Calculating final scores...")
    try:
        final_scores = analyzer.calculate_final_scores()
        print("Final scores calculated successfully\n")
        
        # Generate detailed report
        generate_detailed_report(final_scores, questions)
        
    except Exception as e:
        print(f"Failed to calculate final scores: {e}")
        return
    
    print("\nFull assessment report generated!\n")

def generate_detailed_report(final_scores, questions):
    """生成详细报告"""
    print("\n" + "="*60)
    print("           Full 50-Question Personality Assessment Report")
    print("="*60)
    
    # Big Five Scores
    print("\n[Big Five Personality Dimensions]")
    print("-" * 30)
    big_five_scores = final_scores['big_five']
    traits = [
        ('openness_to_experience', 'Openness'),
        ('conscientiousness', 'Conscientiousness'),
        ('extraversion', 'Extraversion'),
        ('agreeableness', 'Agreeableness'),
        ('neuroticism', 'Neuroticism')
    ]
    
    for trait_key, trait_name in traits:
        score = big_five_scores[trait_key]['score']
        weight = big_five_scores[trait_key]['weight']
        print(f"{trait_name:20} : {score:5.1f}/10.0 (Based on {weight:2d} questions)")
    
    # MBTI Type
    print("\n[MBTI Personality Type]")
    print("-" * 30)
    mbti = final_scores['mbti']
    print(f"Type: {mbti['type']}")
    print(f"Confidence: {mbti['confidence']:.2f}")
    
    # Belbin Team Roles
    print("\n[Belbin Team Roles]")
    print("-" * 30)
    belbin = final_scores['belbin']
    print(f"Primary Role: {belbin['primary_role']}")
    print(f"Secondary Role: {belbin['secondary_role']}")
    
    # Per-question scoring summary
    print("\n[Per-Question Scoring Summary]")
    print("-" * 30)
    per_question_scores = final_scores['per_question_scores']
    print(f"Total questions analyzed: {len(per_question_scores)}")
    
    # Save full report to file
    report_data = {
        'summary': {
            'big_five': big_five_scores,
            'mbti': mbti,
            'belbin': belbin,
            'total_questions_analyzed': len(per_question_scores)
        },
        'per_question_scores': per_question_scores,
        'analysis_summary': final_scores['analysis_summary']
    }
    
    with open('batchAnalysizeTools/full_assessment_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nFull report saved to: batchAnalysizeTools/full_assessment_report.json\n")

if __name__ == "__main__":
    generate_full_assessment_report()