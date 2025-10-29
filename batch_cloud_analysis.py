#!/usr/bin/env python3
"""
Batch cloud analysis script for processing multiple assessment reports with Qwen cloud evaluators
"""

import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import openai
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

class CloudEvaluator:
    def __init__(self, provider: str, model: str, api_key: str, base_url: str = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def create_client(self):
        """Create appropriate client based on provider"""
        if self.provider == "openai":
            return openai.OpenAI(api_key=self.api_key)
        elif self.provider == "dashscope":
            return openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def evaluate(self, prompt: str, system_prompt: str = None):
        """Evaluate using cloud LLM"""
        try:
            client = self.create_client()

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": self.model,
                "provider": self.provider
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model,
                "provider": self.provider
            }

def create_simplified_assessment(full_report: dict) -> dict:
    """Create simplified assessment for analysis"""
    questions = []

    if 'assessment_results' in full_report:
        assessment_results = full_report['assessment_results']
        if isinstance(assessment_results, list):
            for result in assessment_results[:8]:  # Limit to first 8 questions for context
                if 'question_data' in result:
                    question_data = result['question_data'].copy()
                    # Add agent_response from conversation_log
                    if 'conversation_log' in result:
                        for msg in result['conversation_log']:
                            if msg.get('role') == 'assistant':
                                question_data['agent_response'] = msg['content']
                                break
                    questions.append(question_data)

    return {
        "assessment_summary": {
            "total_questions": len(questions),
            "sampled_questions": questions
        }
    }

def analyze_with_cloud_evaluator(input_file: str, evaluator: CloudEvaluator, output_dir: str = "cloud_analysis_results"):
    """Analyze assessment file using cloud evaluator"""
    try:
        # Load assessment data
        with open(input_file, 'r', encoding='utf-8') as f:
            full_report = json.load(f)

        # Create simplified assessment
        report_content = create_simplified_assessment(full_report)

        # System prompt for personality analysis
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

Format your response as JSON:
{
  "personality_assessment": {
    "big_five": {
      "openness_to_experience": {"score": 7, "description": "..."},
      "conscientiousness": {"score": 8, "description": "..."},
      "extraversion": {"score": 6, "description": "..."},
      "agreeableness": {"score": 7, "description": "..."},
      "neuroticism": {"score": 4, "description": "..."}
    },
    "mbti": {
      "type": "ENFJ",
      "description": "..."
    }
  }
}"""

        # Create user prompt
        user_prompt = f"""Please analyze this assessment and provide personality evaluation:

Assessment Data:
{json.dumps(report_content, ensure_ascii=False, indent=2)}

Analyze the agent's responses across different personality dimensions and provide comprehensive Big Five and MBTI assessment."""

        # Run evaluation
        eval_result = evaluator.evaluate(user_prompt, system_prompt)

        if not eval_result.get("success"):
            raise RuntimeError(f"Evaluation failed: {eval_result.get('error')}")

        # Parse response
        try:
            analysis = json.loads(eval_result["response"])
        except json.JSONDecodeError:
            # Try to extract JSON from response
            response_text = eval_result["response"]
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                analysis = json.loads(json_text)
            else:
                analysis = {"raw_response": response_text}

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save results
        report_id = Path(input_file).stem
        result_file = output_path / f"{report_id}_{evaluator.model}_analysis.json"

        result_data = {
            "file": input_file,
            "evaluator": {
                "model": evaluator.model,
                "provider": evaluator.provider
            },
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        }

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "file": str(input_file),
            "output_file": str(result_file),
            "model": evaluator.model
        }

    except Exception as e:
        return {
            "success": False,
            "file": str(input_file),
            "error": str(e),
            "model": evaluator.model
        }

def batch_analyze_files(input_files, evaluator, output_dir, max_workers=3):
    """Batch analyze files with concurrency control"""
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(analyze_with_cloud_evaluator, file, evaluator, output_dir): file
            for file in input_files
        }

        # Process completed tasks
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)

            if result["success"]:
                print(f"✅ {Path(result['file']).name} -> {result['model']}")
            else:
                print(f"❌ {Path(result['file']).name} -> {result['error']}")

            # Add small delay to avoid rate limiting
            time.sleep(0.5)

    return results

def generate_summary_report(results, output_dir):
    """Generate summary report of batch analysis"""
    summary = {
        "summary": {
            "total_files": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "timestamp": datetime.now().isoformat()
        },
        "results": results
    }

    # Save summary JSON
    summary_file = Path(output_dir) / "batch_analysis_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Generate markdown report
    md_content = f"""# Batch Cloud Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Files Processed:** {len(results)}
- **Successful:** {summary['summary']['successful']}
- **Failed:** {summary['summary']['failed']}
- **Success Rate:** {summary['summary']['successful']/len(results)*100:.1f}%

## Successful Analyses

"""

    for result in results:
        if result["success"]:
            md_content += f"- ✅ `{Path(result['file']).name}` -> {result['model']}\n"

    md_content += "\n## Failed Analyses\n\n"

    for result in results:
        if not result["success"]:
            md_content += f"- ❌ `{Path(result['file']).name}` -> {result['error']}\n"

    # Save markdown report
    md_file = Path(output_dir) / "batch_analysis_report.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"📊 Summary report saved to {md_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Batch cloud analysis with Qwen evaluators')
    parser.add_argument('--model', choices=['qwen-long', 'qwen-max', 'both'], default='both',
                       help='Which model to use for analysis')
    parser.add_argument('--sample', type=int, help='Number of files to sample (default: all)')
    parser.add_argument('--filter', help='Filter files by name pattern')
    parser.add_argument('--output', default='cloud_analysis_results', help='Output directory')
    parser.add_argument('--workers', type=int, default=3, help='Number of concurrent workers')

    args = parser.parse_args()

    # Configure Qwen cloud evaluators
    dashscope_key = "sk-ffd03518254b495b8d27e723cd413fc1"

    evaluators = []
    if args.model in ['qwen-long', 'both']:
        evaluators.append(CloudEvaluator("dashscope", "qwen-long", dashscope_key))
    if args.model in ['qwen-max', 'both']:
        evaluators.append(CloudEvaluator("dashscope", "qwen-max", dashscope_key))

    # Get input files
    results_dir = Path("results/results")
    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return

    all_files = list(results_dir.glob("*.json"))

    # Apply filter if specified
    if args.filter:
        all_files = [f for f in all_files if args.filter.lower() in f.name.lower()]

    # Sample files if specified
    if args.sample:
        all_files = all_files[:args.sample]

    print(f"🔍 Found {len(all_files)} files to analyze")
    print(f"🤖 Using {len(evaluators)} evaluators: {[e.model for e in evaluators]}")
    print(f"⚡ Using {args.workers} concurrent workers")

    if not all_files:
        print("❌ No files to analyze")
        return

    total_results = []

    for evaluator in evaluators:
        print(f"\n📊 Running batch analysis with {evaluator.model}...")

        # Create model-specific output directory
        model_output_dir = Path(args.output) / evaluator.model
        model_output_dir.mkdir(parents=True, exist_ok=True)

        # Run batch analysis
        results = batch_analyze_files(all_files, evaluator, model_output_dir, args.workers)
        total_results.extend(results)

        # Show progress
        successful = sum(1 for r in results if r["success"])
        print(f"📈 {evaluator.model}: {successful}/{len(results)} files processed successfully")

        # Small delay between different models
        if len(evaluators) > 1:
            time.sleep(2)

    # Generate summary report
    print(f"\n📋 Generating summary report...")
    generate_summary_report(total_results, args.output)

    # Final summary
    total_successful = sum(1 for r in total_results if r["success"])
    total_processed = len(total_results)

    print(f"\n🎉 Batch analysis complete!")
    print(f"✅ Total Successful: {total_successful}/{total_processed} ({total_successful/total_processed*100:.1f}%)")
    print(f"📁 Results saved to: {args.output}")

if __name__ == "__main__":
    main()