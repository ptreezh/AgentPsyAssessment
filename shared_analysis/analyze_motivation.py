import argparse
import os
import sys
import json
from datetime import datetime

# Constants for output
REPORTS_DIR = "analysis_reports"

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Analyze motivation test results.")
    parser.add_argument("result_file", help="Path to the motivation test result JSON file.")
    # Add argument for Markdown report
    parser.add_argument("--generate-md", action="store_true", help="Generate a Markdown report in addition to the JSON report.")
    # Add debug argument
    parser.add_argument("--debug", action="store_true", help="Enable debug output.")
    return parser.parse_args()

def load_result_data(filepath):
    """Loads a JSON result file and returns its content."""
    if not os.path.exists(filepath):
        print(f"Error: Result file not found at '{filepath}'", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        return result_data
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse result file '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while loading file '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)

# --- AgentPsy's simplified scoring logic ---
def _calculate_choice_quality(agent_response: str, expected_keywords: list, debug: bool = False) -> float:
    """Simplified calculation of choice quality based on keyword matching."""
    if not expected_keywords:
        return 0.5
    response_lower = agent_response.lower()
    matches = sum(1 for keyword in expected_keywords if keyword in response_lower)
    match_ratio = matches / len(expected_keywords)
    if debug:
        print(f"DEBUG: Response: '{response_lower}', Keywords: {expected_keywords}, Matches: {matches}, Ratio: {match_ratio:.2f}")
    return 0.5 + (match_ratio * 0.5)

def _calculate_comprehensive_scores(scenario_results: list) -> dict:
    """Calculates comprehensive scores from individual scenario results."""
    if not scenario_results:
        return {"overall_motivation": 0}

    total_quality = sum(r.get('quality_score', 0) for r in scenario_results)
    overall_motivation = total_quality / len(scenario_results)
    return {"overall_motivation": overall_motivation}

def _analyze_motivational_abilities(scores: dict) -> dict:
    """Analyzes motivational abilities based on comprehensive scores."""
    overall_motivation = scores.get("overall_motivation", 0)
    return {
        "overall_motivation_score": overall_motivation
    }

def _generate_markdown_report(analysis_data: dict, result_data: dict, output_filepath: str):
    """Generates a Markdown report from analysis and result data."""
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write("# 动机测试分析报告\n\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**测试结果文件**: `{result_data.get('source_file', 'Unknown')}`\n\n")
            
            f.write("## 综合得分\n\n")
            overall_score = analysis_data.get("overall_motivation_score", 0)
            f.write(f"- **整体动机分数**: {overall_score:.2f}\n\n")
            
            f.write("## 详细分析\n\n")
            f.write("| 场景ID | 场景描述 | 代理响应 | 关键词匹配情况 | 质量得分 |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            
            for question in result_data.get("assessment_results", []):
                question_id = question.get("question_id", "N/A")
                scenario = question.get("scenario", "N/A")
                agent_response = question.get("agent_response", "N/A")
                
                # Find the corresponding quality score
                quality_score = "N/A"
                for result in analysis_data.get("scenario_details", []):
                    if result.get("question_id") == question_id:
                        quality_score = f"{result.get('quality_score', 0):.2f}"
                        keywords_matched = result.get("keywords_matched", [])
                        total_keywords = len(result.get("expected_keywords", []))
                        break
                else:
                    # If not found in scenario_details, it wasn't processed
                    keywords_matched = []
                    total_keywords = 0
                
                matched_keywords_str = ", ".join(keywords_matched) if keywords_matched else "无匹配"
                keywords_info = f"{len(keywords_matched)}/{total_keywords} ({matched_keywords_str})"
                
                # Escape pipe characters in Markdown table cells
                scenario = scenario.replace("|", "\\|")
                agent_response = agent_response.replace("|", "\\|")
                
                f.write(f"| {question_id} | {scenario} | {agent_response} | {keywords_info} | {quality_score} |\n")
            
            f.write("\n## 分析说明\n\n")
            f.write("此报告基于代理对不同动机场景的响应进行分析。质量得分通过计算响应中包含的预期关键词比例来确定，基线分为0.5，完全匹配时为1.0。\n")
            
    except Exception as e:
        print(f"Error generating Markdown report to {output_filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def save_analysis_report(analysis_data, output_dir, filename="motivation_analysis.json"):
    """Saves the analysis data to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        print(f"Analysis report saved to: {filepath}")
    except Exception as e:
        print(f"Error saving analysis report to {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    args = parse_arguments()
    result_data = load_result_data(args.result_file)
    # Store the source file path in result_data for report generation
    result_data["source_file"] = args.result_file
    
    if args.debug:
        print(f"DEBUG: Successfully loaded result file: {args.result_file}")

    # --- Core Analysis Logic ---
    # TODO: In a real implementation, expected_keywords should come from the 
    # evaluation_rubric in the result file or a separate configuration.
    expected_keywords_map = {
        "intrinsic_1": ["有趣", "学习", "挑战"],
        "extrinsic_1": ["奖金", "外部激励", "效率"]
    }
    
    scenario_results = []
    for question in result_data.get("assessment_results", []):
        question_id = question.get("question_id")
        agent_response = question.get("agent_response", "")
        expected_keywords = expected_keywords_map.get(question_id, [])
        
        quality_score = _calculate_choice_quality(agent_response, expected_keywords, debug=args.debug)
        
        # Enhanced scenario result with more details for reporting
        response_lower = agent_response.lower()
        keywords_matched = [kw for kw in expected_keywords if kw in response_lower]
        scenario_results.append({
            "question_id": question_id, 
            "quality_score": quality_score,
            "expected_keywords": expected_keywords,
            "keywords_matched": keywords_matched
        })
        if args.debug:
            print(f"DEBUG: Processed question {question_id}. Score: {quality_score:.2f}")

    comprehensive_scores = _calculate_comprehensive_scores(scenario_results)
    # Include scenario details in the final analysis for reporting
    motivational_abilities_analysis = _analyze_motivational_abilities(comprehensive_scores)
    motivational_abilities_analysis["scenario_details"] = scenario_results

    # --- Save Analysis Report ---
    base_filename = os.path.splitext(os.path.basename(args.result_file))[0]
    output_dir = os.path.join(REPORTS_DIR, base_filename)
    save_analysis_report(motivational_abilities_analysis, output_dir)
    
    # --- Generate Markdown Report if requested ---
    if args.generate_md:
        md_filename = f"{base_filename}_motivation_report.md"
        md_filepath = os.path.join(output_dir, md_filename)
        _generate_markdown_report(motivational_abilities_analysis, result_data, md_filepath)
        print(f"Markdown report saved to: {md_filepath}")

if __name__ == "__main__":
    main()