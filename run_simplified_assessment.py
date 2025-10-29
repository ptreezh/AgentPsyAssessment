#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified complete assessment script - Analyze first few segments only
"""

import json
import sys
import os
import time

def run_simplified_assessment():
    """Run simplified assessment (first 3 segments only)"""
    print("=" * 60)
    print("Running simplified assessment (first 3 segments)")
    print("This will analyze 6 questions to demonstrate the complete process")
    print("=" * 60)
    print("Start time: " + time.strftime('%Y-%m-%d %H:%M:%S'))
    
    # Record start time
    start_time = time.time()
    
    try:
        # Set environment variable to fix Windows encoding issue
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Import necessary modules
        sys.path.append('batchAnalysizeTools')
        from batch_segmented_analysis import BatchSegmentedPersonalityAnalyzer
        
        # Load assessment data
        print("\n1. Loading assessment file...")
        with open("results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json", 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        print("   ✓ File loaded successfully")
        
        # Initialize analyzer
        print("\n2. Initializing analyzer...")
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=2,  # 2 questions per segment
            evaluator_name="gemma3",
            base_url="http://localhost:11434"
        )
        print("   ✓ Analyzer initialized successfully")
        
        # Extract questions
        print("\n3. Extracting questions...")
        questions = analyzer.extract_questions(assessment_data)
        print("   ✓ Successfully extracted " + str(len(questions)) + " questions")
        
        # Create segments
        print("\n4. Creating segments...")
        segments = analyzer.create_segments(questions)
        print("   ✓ Successfully created " + str(len(segments)) + " segments")
        
        # Analyze first 3 segments only (for demonstration)
        print("\n5. Analyzing first 3 segments (6 questions)...")
        successful_segments = 0
        total_questions_analyzed = 0
        segments_to_analyze = min(3, len(segments))  # Analyze first 3 segments or all if less than 3
        
        for i in range(segments_to_analyze):
            segment = segments[i]
            print("   Analyzing segment " + str(i+1) + "/" + str(segments_to_analyze) + " (" + str(len(segment)) + " questions)...")
            try:
                segment_analysis = analyzer.analyze_segment(segment, i+1)
                if 'llm_response' in segment_analysis:
                    analyzer.accumulate_scores(segment_analysis['llm_response'])
                    successful_segments += 1
                    total_questions_analyzed += len(segment)
                    print("     ✓ Segment " + str(i+1) + " analyzed successfully")
                else:
                    print("     ✗ Segment " + str(i+1) + " analysis failed")
            except Exception as e:
                print("     ✗ Segment " + str(i+1) + " analysis error: " + str(e))
                continue
        
        print("\n   ✓ Successfully analyzed " + str(successful_segments) + "/" + str(segments_to_analyze) + " segments")
        print("   ✓ Total questions analyzed: " + str(total_questions_analyzed))
        
        # Calculate final scores
        print("\n6. Calculating final scores...")
        final_scores = analyzer.calculate_final_scores()
        print("   ✓ Final scores calculated successfully")
        
        # Generate report
        print("\n7. Generating sample report...")
        generate_sample_report(final_scores, total_questions_analyzed)
        
        # Record end time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("Simplified assessment completed!")
        print("Analyzed " + str(total_questions_analyzed) + " questions from first " + str(segments_to_analyze) + " segments")
        print("End time: " + time.strftime('%Y-%m-%d %H:%M:%S'))
        print("Total time: " + str(round(elapsed_time, 2)) + " seconds")
        print("=" * 60)
        
        # Show what a full assessment would produce
        print("\nNote: This was a simplified assessment analyzing only the first 3 segments.")
        print("A full assessment would analyze all 25 segments (50 questions) and produce:")
        print("  - Complete Big Five personality dimensions scoring")
        print("  - Full MBTI personality type mapping")
        print("  - Complete Belbin team roles analysis")
        print("  - Detailed per-question scoring for all 50 questions")
        
    except Exception as e:
        print("\n❌ Error during execution: " + str(e))
        import traceback
        traceback.print_exc()

def generate_sample_report(final_scores, questions_analyzed):
    """Generate sample report"""
    # Big Five Scores
    print("\n[Big Five Personality Dimensions (Sample)]")
    print("-" * 50)
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
    print("\n[MBTI Personality Type (Sample)]")
    print("-" * 50)
    mbti = final_scores['mbti']
    print(f"Type: {mbti['type']}")
    print(f"Confidence: {mbti['confidence']:.2f}")
    
    # Belbin Team Roles
    print("\n[Belbin Team Roles (Sample)]")
    print("-" * 50)
    belbin = final_scores['belbin']
    print(f"Primary Role: {belbin['primary_role']}")
    print(f"Secondary Role: {belbin['secondary_role']}")
    
    # Save sample report to file
    report_data = {
        'summary': {
            'big_five': big_five_scores,
            'mbti': mbti,
            'belbin': belbin,
            'total_questions_analyzed': questions_analyzed
        },
        'per_question_scores': final_scores['per_question_scores'][:6],  # Only first 6 questions
        'analysis_summary': final_scores['analysis_summary']
    }
    
    # Save JSON format report
    with open('batchAnalysizeTools/sample_assessment_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print("\n📄 Sample JSON report saved to: batchAnalysizeTools/sample_assessment_report.json")
    
    # Generate Markdown format report
    generate_sample_markdown_report(report_data)
    print("📝 Sample Markdown report saved to: batchAnalysizeTools/sample_assessment_report.md")

def generate_sample_markdown_report(report_data):
    """Generate sample Markdown format report"""
    md_content = "# Sample Personality Assessment Report\n\n"
    md_content += "## Overview\n\n"
    md_content += "This is a sample report based on analyzing the first 6 questions from a 50-question personality assessment.\n"
    md_content += "A full assessment would analyze all 50 questions with strict 1-3-5 scoring standard.\n\n"
    
    md_content += "## Big Five Personality Dimensions (Sample)\n\n"
    md_content += "| Dimension | Score | Question Count |\n"
    md_content += "|-----------|-------|----------------|\n"
    
    big_five = report_data['summary']['big_five']
    traits = [
        ('openness_to_experience', 'Openness'),
        ('conscientiousness', 'Conscientiousness'),
        ('extraversion', 'Extraversion'),
        ('agreeableness', 'Agreeableness'),
        ('neuroticism', 'Neuroticism')
    ]
    
    for trait_key, trait_name in traits:
        score = big_five[trait_key]['score']
        weight = big_five[trait_key]['weight']
        md_content += f"| {trait_name} | {score:.1f}/10.0 | {weight} |\n"
    
    md_content += f"\n## MBTI Personality Type (Sample)\n\n"
    md_content += f"- Type: {report_data['summary']['mbti']['type']}\n"
    md_content += f"- Confidence: {report_data['summary']['mbti']['confidence']:.2f}\n\n"
    
    md_content += f"## Belbin Team Roles (Sample)\n\n"
    md_content += f"- Primary Role: {report_data['summary']['belbin']['primary_role']}\n"
    md_content += f"- Secondary Role: {report_data['summary']['belbin']['secondary_role']}\n\n"
    
    md_content += "## Per-Question Detailed Scoring (First 6 Questions)\n\n"
    md_content += "The following is the detailed scoring for the first 6 questions:\n"
    
    for i in range(min(6, len(report_data['per_question_scores']))):
        score = report_data['per_question_scores'][i]
        md_content += f"\n### Question {i+1}: {score['dimension']}\n\n"
        md_content += f"- Question ID: {score['question_id']}\n"
        md_content += "- Big Five Scores:\n"
        
        for trait, trait_score in score['big_five_scores'].items():
            # Ensure score is 1, 3, or 5
            fixed_score = trait_score['score']
            if fixed_score not in [1, 3, 5]:
                # Map score to nearest 1-3-5 value
                if fixed_score < 2:
                    fixed_score = 1
                elif fixed_score < 4:
                    fixed_score = 3
                else:
                    fixed_score = 5
            md_content += f"  - {trait}: {fixed_score} ({trait_score['evidence']})\n"
    
    with open('batchAnalysizeTools/sample_assessment_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    run_simplified_assessment()