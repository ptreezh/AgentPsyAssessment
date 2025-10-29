#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete 50-question assessment script - Using 1-3-5 scoring standard
"""

import json
import sys
import os
import time

def run_complete_assessment():
    """Run complete 50-question assessment"""
    print("=" * 60)
    print("Starting complete 50-question personality assessment")
    print("Scoring standard: Strictly following 1-3-5 three-level scoring")
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
        
        # Analyze all segments
        print("\n5. Starting analysis of all segments...")
        successful_segments = 0
        total_questions_analyzed = 0
        
        for i in range(len(segments)):
            segment = segments[i]
            print("   Analyzing segment " + str(i+1) + "/" + str(len(segments)) + " (" + str(len(segment)) + " questions)...")
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
        
        print("\n   ✓ Successfully analyzed " + str(successful_segments) + "/" + str(len(segments)) + " segments")
        print("   ✓ Total questions analyzed: " + str(total_questions_analyzed))
        
        # Calculate final scores
        print("\n6. Calculating final scores...")
        final_scores = analyzer.calculate_final_scores()
        print("   ✓ Final scores calculated successfully")
        
        # Generate report
        print("\n7. Generating complete report...")
        generate_complete_report(final_scores)
        
        # Record end time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("Complete 50-question assessment finished!")
        print("End time: " + time.strftime('%Y-%m-%d %H:%M:%S'))
        print("Total time: " + str(round(elapsed_time, 2)) + " seconds (" + str(round(elapsed_time/60, 2)) + " minutes)")
        print("=" * 60)
        
    except Exception as e:
        print("\n❌ Error during execution: " + str(e))
        import traceback
        traceback.print_exc()

def generate_complete_report(final_scores):
    """Generate complete report"""
    # Big Five Scores
    print("\n[Big Five Personality Dimensions]")
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
    print("\n[MBTI Personality Type]")
    print("-" * 50)
    mbti = final_scores['mbti']
    print(f"Type: {mbti['type']}")
    print(f"Confidence: {mbti['confidence']:.2f}")
    
    # Belbin Team Roles
    print("\n[Belbin Team Roles]")
    print("-" * 50)
    belbin = final_scores['belbin']
    print(f"Primary Role: {belbin['primary_role']}")
    print(f"Secondary Role: {belbin['secondary_role']}")
    
    # Save complete report to file
    report_data = {
        'summary': {
            'big_five': big_five_scores,
            'mbti': mbti,
            'belbin': belbin,
            'total_questions_analyzed': len(final_scores['per_question_scores'])
        },
        'per_question_scores': final_scores['per_question_scores'],
        'analysis_summary': final_scores['analysis_summary']
    }
    
    # Save JSON format report
    with open('batchAnalysizeTools/complete_assessment_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print("\n📄 JSON format complete report saved to: batchAnalysizeTools/complete_assessment_report.json")
    
    # Generate Markdown format report
    generate_markdown_report(report_data)
    print("📝 Markdown format complete report saved to: batchAnalysizeTools/complete_assessment_report.md")
    
    # Generate summary report
    generate_summary_report(report_data)
    print("📋 Summary report saved to: batchAnalysizeTools/assessment_summary.txt")

def generate_markdown_report(report_data):
    """Generate Markdown format report"""
    md_content = "# Complete 50-Question Personality Assessment Report\n\n"
    md_content += "## Overview\n\n"
    md_content += "This report is based on a complete 50-question personality assessment analyzed using the Gemma3 model with strict 1-3-5 three-level scoring standard.\n\n"
    
    md_content += "## Big Five Personality Dimensions\n\n"
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
    
    md_content += f"\n## MBTI Personality Type\n\n"
    md_content += f"- Type: {report_data['summary']['mbti']['type']}\n"
    md_content += f"- Confidence: {report_data['summary']['mbti']['confidence']:.2f}\n\n"
    
    md_content += f"## Belbin Team Roles\n\n"
    md_content += f"- Primary Role: {report_data['summary']['belbin']['primary_role']}\n"
    md_content += f"- Secondary Role: {report_data['summary']['belbin']['secondary_role']}\n\n"
    
    md_content += "## Per-Question Detailed Scoring\n\n"
    md_content += "The following is the detailed scoring for all questions (strictly following 1-3-5 scoring standard):\n"
    
    for i in range(len(report_data['per_question_scores'])):
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
    
    with open('batchAnalysizeTools/complete_assessment_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

def generate_summary_report(report_data):
    """Generate summary report"""
    summary_content = "Complete 50-Question Personality Assessment Summary Report\n"
    summary_content += "=" * 50 + "\n\n"
    
    summary_content += "Big Five Personality Dimensions:\n"
    summary_content += "-" * 30 + "\n"
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
        summary_content += f"{trait_name}: {score:.1f}/10.0\n"
    
    summary_content += f"\nMBTI Personality Type: {report_data['summary']['mbti']['type']}\n"
    summary_content += f"Confidence: {report_data['summary']['mbti']['confidence']:.2f}\n\n"
    
    summary_content += f"Belbin Team Roles:\n"
    summary_content += f"Primary Role: {report_data['summary']['belbin']['primary_role']}\n"
    summary_content += f"Secondary Role: {report_data['summary']['belbin']['secondary_role']}\n"
    
    with open('batchAnalysizeTools/assessment_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary_content)

if __name__ == "__main__":
    run_complete_assessment()