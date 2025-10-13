import os
import json
import argparse
import time
from datetime import datetime
from dotenv import load_dotenv
import openai
import anthropic
from pathlib import Path

# Import Ollama evaluator
try:
    from .ollama_evaluator import (
        create_ollama_evaluator, 
        load_ollama_config, 
        get_ollama_model_config,
        get_ollama_evaluators
    )
    OLLAMA_AVAILABLE = True
except ImportError:
    try:
        from ollama_evaluator import (
            create_ollama_evaluator, 
            load_ollama_config, 
            get_ollama_model_config,
            get_ollama_evaluators
        )
        OLLAMA_AVAILABLE = True
    except ImportError:
        OLLAMA_AVAILABLE = False

def create_simplified_assessment(full_report: dict) -> dict:
    """Create a simplified version of the assessment report to avoid context window limits"""
    # Import the segmented analyzer
    try:
        from segmented_analysis import SegmentedPersonalityAnalyzer
        analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=8)

        # Extract questions
        # Extract questions using the same logic as segmented analyzer
        if 'assessment_results' in full_report:
            assessment_results = full_report['assessment_results']
            if isinstance(assessment_results, list):
                # 检查是否是问题对象列表（每个对象包含question_data）
                if len(assessment_results) > 0 and isinstance(assessment_results[0], dict):
                    if 'question_data' in assessment_results[0]:
                        # 从question_data中提取问题
                        questions = []
                        for result in assessment_results:
                            if 'question_data' in result:
                                question_data = result['question_data'].copy()
                                # 添加agent_response从conversation_log中提取
                                if 'conversation_log' in result:
                                    for msg in result['conversation_log']:
                                        if msg.get('role') == 'assistant':
                                            question_data['agent_response'] = msg['content']
                                            break
                                questions.append(question_data)
                    else:
                        # 如果assessment_results本身就是问题列表
                        questions = assessment_results
                else:
                    questions = assessment_results
            elif isinstance(assessment_results, dict) and 'questions' in assessment_results:
                questions = assessment_results['questions']
            else:
                questions = []
        elif 'questions' in full_report:
            questions = full_report['questions']
        else:
            return {
                "assessment_summary": {
                    "error": "No questions found in assessment data",
                    "structure": list(full_report.keys())
                }
            }

        # Use segmented approach to create summary
        segments = analyzer.create_segments(questions)

        # Sample from first segment for quick analysis
        if segments:
            sampled_questions = []
            for question in segments[0][:6]:  # Take first 6 questions from first segment
                sampled_questions.append({
                    "dimension": question.get('dimension', 'Unknown'),
                    "scenario": question['scenario'][:150] + "..." if len(question['scenario']) > 150 else question['scenario'],
                    "response": question['agent_response'][:400] + "..." if len(question['agent_response']) > 400 else question['agent_response'],
                    "rubric_description": question.get('evaluation_rubric', {}).get('description', '')
                })

            return {
                "assessment_summary": {
                    "total_questions": len(questions),
                    "unique_dimensions": list(set(q.get('dimension', 'Unknown') for q in questions)),
                    "sampled_questions_count": len(sampled_questions),
                    "segmented_analysis": {
                        "total_segments": len(segments),
                        "first_segment_size": len(segments[0]) if segments else 0
                    },
                    "sampled_questions": sampled_questions
                }
            }
        else:
            return {
                "assessment_summary": {
                    "error": "No segments created",
                    "total_questions": len(questions)
                }
            }

    except ImportError:
        # Fallback to simple sampling if segmented analyzer is not available
        return create_simple_sampled_assessment(full_report)

def create_simple_sampled_assessment(full_report: dict) -> dict:
    """Fallback simple sampling method"""
    # Extract questions using the same logic as segmented analyzer
    if 'assessment_results' in full_report:
        assessment_results = full_report['assessment_results']
        if isinstance(assessment_results, list):
            # 检查是否是问题对象列表（每个对象包含question_data）
            if len(assessment_results) > 0 and isinstance(assessment_results[0], dict):
                if 'question_data' in assessment_results[0]:
                    # 从question_data中提取问题
                    questions = []
                    for result in assessment_results:
                        if 'question_data' in result:
                            question_data = result['question_data'].copy()
                            # 添加agent_response从conversation_log中提取
                            if 'conversation_log' in result:
                                for msg in result['conversation_log']:
                                    if msg.get('role') == 'assistant':
                                        question_data['agent_response'] = msg['content']
                                        break
                            questions.append(question_data)
                else:
                    # 如果assessment_results本身就是问题列表
                    questions = assessment_results
            else:
                questions = assessment_results
        elif isinstance(assessment_results, dict) and 'questions' in assessment_results:
            questions = assessment_results['questions']
        else:
            questions = []
    elif 'questions' in full_report:
        questions = full_report['questions']
    else:
        return {
            "assessment_summary": {
                "error": "No questions found in assessment data",
                "structure": list(full_report.keys())
            }
        }

    # Simple sampling - take first 8 questions
    sampled_questions = []
    for question in questions[:8]:
        sampled_questions.append({
            "dimension": question.get('dimension', 'Unknown'),
            "scenario": question['scenario'][:150] + "..." if len(question['scenario']) > 150 else question['scenario'],
            "response": question['agent_response'][:400] + "..." if len(question['agent_response']) > 400 else question['agent_response'],
            "rubric_description": question.get('evaluation_rubric', {}).get('description', '')
        })

    return {
        "assessment_summary": {
            "total_questions": len(questions),
            "unique_dimensions": list(set(q.get('dimension', 'Unknown') for q in questions)),
            "sampled_questions_count": len(sampled_questions),
            "sampled_questions": sampled_questions
        }
    }

def analyze_single_file(input_file: str, output_dir: str) -> bool:
    """Analyze a single assessment file and generate Big5+MBTI outputs with logs"""
    try:
        input_path = Path(input_file)
        report_id = input_path.stem

        eval_dir = Path(output_dir)
        # Place logs in a subdirectory of the specific evaluation output
        logs_dir = eval_dir / "logs"

        eval_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama evaluator is not available. Cannot perform analysis.")

        with open(input_path, 'r', encoding='utf-8') as f:
            full_report = json.load(f)

        # Create a simplified version to avoid context window limits
        report_content = create_simplified_assessment(full_report)

        evaluators = get_ollama_evaluators()
        if not evaluators:
            raise ValueError("No Ollama evaluators configured in config/ollama_config.json")
        evaluator_name = list(evaluators.keys())[0]
        ollama_evaluator = create_ollama_evaluator(evaluator_name)
        if not ollama_evaluator:
            raise ConnectionError(f"Failed to create or connect to Ollama evaluator: {evaluator_name}")

        system_prompt = """You are a psychology expert specializing in Big Five and MBTI personality assessment.

I will provide you with a psychological assessment report containing questions and responses from an AI agent. Your task is to analyze these responses and provide a NEW personality evaluation.

CRITICAL INSTRUCTIONS:
- DO NOT copy or return the original data
- DO NOT include fields like "assessment_metadata", "questions", "evaluation_rubric", etc.
- You MUST analyze the content and generate NEW psychological insights
- Your response should ONLY contain the personality assessment with Big Five scores and MBTI type

Based on the agent's responses, analyze their personality traits and provide:

1. Big Five personality traits with scores (1-10 scale):
   - Openness to Experience (O) - creativity, curiosity, openness to new experiences
   - Conscientiousness (C) - organization, responsibility, self-discipline
   - Extraversion (E) - sociability, assertiveness, enthusiasm
   - Agreeableness (A) - cooperation, trust, compassion
   - Neuroticism (N) - emotional stability, anxiety, moodiness

2. MBTI personality type (4-letter code like ENFJ, ISTP, etc.)

Return ONLY your psychological analysis in this exact JSON format:
{
  "personality_assessment": {
    "big_five": {
      "openness_to_experience": {"score": 7, "description": "Shows high creativity and openness to new ideas"},
      "conscientiousness": {"score": 6, "description": "Moderately organized and responsible"},
      "extraversion": {"score": 8, "description": "Very sociable and assertive"},
      "agreeableness": {"score": 7, "description": "Cooperative and compassionate"},
      "neuroticism": {"score": 4, "description": "Emotionally stable and calm"}
    },
    "mbti": {
      "type": "ENFJ",
      "description": "Warm, empathetic, and responsible leader"
    }
  }
}

Now analyze the provided assessment data and give me your professional psychological evaluation. Remember: create NEW analysis, don't copy the input!"""
        user_prompt = json.dumps(report_content, ensure_ascii=False)

        eval_result = ollama_evaluator.evaluate_json_response(
            model_name=evaluators[evaluator_name]['model'],
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        if not eval_result.get("success"):
            with open(logs_dir / f"{report_id}.log", "w", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] Analysis failed: {eval_result.get('error')}\n")
            raise RuntimeError(f"Evaluation failed: {eval_result.get('error', 'Unknown error')}")

        analysis = eval_result["response"]
        with open(logs_dir / f"{report_id}.log", "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Analysis successful. Response: {json.dumps(analysis, ensure_ascii=False)}\n")

        # --- Robust Data Extraction ---
        final_analysis = {}
        
        # Find the Big 5 data, checking multiple possible keys
        big_five_data = None
        if 'personality_assessment' in analysis and 'big_five' in analysis['personality_assessment']:
            big_five_data = analysis['personality_assessment']['big_five']
        elif 'Big5' in analysis:
            big_five_data = analysis['Big5']
        elif 'big_five' in analysis:
            big_five_data = analysis['big_five']
        
        # Find the MBTI data
        mbti_data = None
        if 'personality_assessment' in analysis and 'mbti' in analysis['personality_assessment']:
            mbti_data = analysis['personality_assessment']['mbti']
        elif 'MBTI' in analysis:
            mbti_data = analysis['MBTI']
        elif 'mbti' in analysis:
            mbti_data = analysis['mbti']

        # Process extracted data
        trait_mapping = {
            'openness_to_experience': 'O',
            'openness': 'O',
            'conscientiousness': 'C',
            'extraversion': 'E',
            'agreeableness': 'A',
            'neuroticism': 'N'
        }
        final_analysis['big5'] = {}
        if big_five_data:
            for trait, score_data in big_five_data.items():
                letter = trait_mapping.get(trait.lower())
                if letter:
                    score = score_data.get('score') if isinstance(score_data, dict) else score_data
                    final_analysis['big5'][letter] = score

        final_analysis['mbti'] = mbti_data.get('type', 'N/A') if mbti_data else 'N/A'

        # Write final outputs
        with open(eval_dir / "analysis.json", "w", encoding="utf-8") as f:
            json.dump(final_analysis, f, ensure_ascii=False, indent=2)
        
        with open(eval_dir / "analysis.md", "w", encoding="utf-8") as f:
            f.write(f"# Analysis Report: {report_id}\n\n")
            f.write(f"**Big Five Scores:**\n")
            for trait, score in final_analysis['big5'].items():
                f.write(f"- {trait}: {score}\n")
            f.write(f"\n**MBTI Type:** {final_analysis['mbti']}\n")
        
        return True
    except Exception as e:
        # Log the exception to the log file if possible
        try:
            logs_dir = Path(output_dir) / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            report_id = Path(input_file).stem
            with open(logs_dir / f"{report_id}.log", "w", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] Analysis CRASHED: {e}\n")
        except Exception:
            pass
        print(f"Analysis failed for {input_file}: {e}")
        return False

# The rest of the file is omitted for brevity as it is unchanged.