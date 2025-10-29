#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run full assessment with fixed 1-3-5 scoring standard
"""

import json
import sys
import os
import time

def run_fixed_full_assessment():
    """Run full assessment with fixed scoring standard"""
    print("=" * 60)
    print("Starting full 50-question assessment with 1-3-5 scoring")
    print("=" * 60)
    print("Start time: " + time.strftime('%Y-%m-%d %H:%M:%S'))
    
    # Record start time
    start_time = time.time()
    
    try:
        # Set environment variable to fix Windows encoding issue
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Import necessary modules
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'batchAnalysizeTools'))
        from batch_segmented_analysis import BatchSegmentedPersonalityAnalyzer
        
        # Load assessment data
        print("1. Loading assessment file...")
        with open("results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json", 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        print("   File loaded successfully")
        
        # Initialize analyzer
        print("2. Initializing analyzer...")
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=2,
            evaluator_name="gemma3",
            base_url="http://localhost:11434"
        )
        print("   Analyzer initialized successfully")
        
        # Extract questions
        print("3. Extracting questions...")
        questions = analyzer.extract_questions(assessment_data)
        print("   Successfully extracted " + str(len(questions)) + " questions")
        
        # Create segments
        print("4. Creating segments...")
        segments = analyzer.create_segments(questions)
        print("   Successfully created " + str(len(segments)) + " segments")
        
        # Analyze all segments
        print("5. Analyzing all segments...")
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
                    print("     Segment " + str(i+1) + " analyzed successfully")
                else:
                    print("     Segment " + str(i+1) + " analysis failed")
            except Exception as e:
                print("     Segment " + str(i+1) + " analysis error: " + str(e))
                continue
        
        print("   Successfully analyzed " + str(successful_segments) + "/" + str(len(segments)) + " segments")
        print("   Total questions analyzed: " + str(total_questions_analyzed))
        
        # Calculate final scores
        print("6. Calculating final scores...")
        final_scores = analyzer.calculate_final_scores()
        print("   Final scores calculated successfully")
        
        # Generate report
        print("7. Generating final report...")
        generate_fixed_final_report(final_scores)
        
        # Record end time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("=" * 60)
        print("Full assessment with 1-3-5 scoring completed!")
        print("End time: " + time.strftime('%Y-%m-%d %H:%M:%S'))
        print("Total time: " + str(round(elapsed_time, 2)) + " seconds (" + str(round(elapsed_time/60, 2)) + " minutes)")
        print("=" * 60)
        
    except Exception as e:
        print("Error during execution: " + str(e))
        import traceback
        traceback.print_exc()

def generate_fixed_final_report(final_scores):
    """Generate final report"""
    # Big Five Scores
    print("")
    print("[Big Five Personality Dimensions]")
    print("-" * 40)
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
        print(trait_name + " : " + str(round(score, 1)) + "/10.0 (Based on " + str(weight) + " questions)")
    
    # MBTI Type
    print("")
    print("[MBTI Personality Type]")
    print("-" * 40)
    mbti = final_scores['mbti']
    print("Type: " + mbti['type'])
    print("Confidence: " + str(round(mbti['confidence'], 2)))
    
    # Belbin Team Roles
    print("")
    print("[Belbin Team Roles]")
    print("-" * 40)
    belbin = final_scores['belbin']
    print("Primary Role: " + belbin['primary_role'])
    print("Secondary Role: " + belbin['secondary_role'])
    
    # Save JSON report
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
    
    with open('batchAnalysizeTools/fixed_full_assessment_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print("")
    print("JSON report saved to: batchAnalysizeTools/fixed_full_assessment_report.json")
    
    # Generate Markdown report
    generate_fixed_markdown_report(report_data)
    print("Markdown report saved to: batchAnalysizeTools/fixed_full_assessment_report.md")

def generate_fixed_markdown_report(report_data):
    """Generate Markdown report"""
    md_content = "# Full 50-Question Personality Assessment Report (1-3-5 Scoring)\n\n"
    md_content += "## Overview\n\n"
    md_content += "This report is based on a full 50-question personality assessment analyzed using the Gemma3 model with strict 1-3-5 scoring standard.\n\n"
    
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
        md_content += "| " + trait_name + " | " + str(round(score, 1)) + "/10.0 | " + str(weight) + " |\n"
    
    md_content += "\n## MBTI Personality Type\n\n"
    md_content += "- Type: " + report_data['summary']['mbti']['type'] + "\n"
    md_content += "- Confidence: " + str(round(report_data['summary']['mbti']['confidence'], 2)) + "\n\n"
    
    md_content += "## Belbin Team Roles\n\n"
    md_content += "- Primary Role: " + report_data['summary']['belbin']['primary_role'] + "\n"
    md_content += "- Secondary Role: " + report_data['summary']['belbin']['secondary_role'] + "\n\n"
    
    md_content += "## Per-Question Detailed Scoring\n\n"
    md_content += "Detailed scoring for all questions (strictly following 1-3-5 scoring standard):\n"
    
    for i in range(len(report_data['per_question_scores'])):
        score = report_data['per_question_scores'][i]
        md_content += "\n### Question " + str(i+1) + ": " + score['dimension'] + "\n\n"
        md_content += "- Question ID: " + score['question_id'] + "\n"
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
            md_content += "  - " + trait + ": " + str(fixed_score) + " (" + trait_score['evidence'] + ")\n"
    
    with open('batchAnalysizeTools/fixed_full_assessment_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    run_fixed_full_assessment()