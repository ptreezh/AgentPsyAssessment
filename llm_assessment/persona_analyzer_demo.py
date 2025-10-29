import os
import sys

# Add the persona_analyzer directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'persona_analyzer'))

from data_loader import ReportParser, RoleDefinitionParser
from analyzer import AnalysisService
from interpretation_engine import InterpretationEngine
from reporter import ReportGenerator


def main():
    """
    Main function to demonstrate the usage of the Persona-Analyzer tool.
    """
    print("Persona-Analyzer: LLM Personality Conformance Analysis Tool")
    print("=" * 60)
    
    # For demonstration purposes, we'll create some mock data
    # In a real scenario, you would point these to your actual data directories
    reports_dir = "./analysis_reports"  # 替换为你的实际报告目录
    roles_dir = "./llm_assessment/roles"  # 替换为你的实际角色定义目录
    output_file = "./persona_analysis_report.md"  # 输出报告文件
    
    # Check if directories exist
    if not os.path.exists(reports_dir):
        print(f"Warning: Reports directory '{reports_dir}' not found.")
        print("Please provide the correct path to your analysis reports.")
        return
        
    if not os.path.exists(roles_dir):
        print(f"Warning: Roles directory '{roles_dir}' not found.")
        print("Please provide the correct path to your role definitions.")
        return
    
    try:
        # 1. Data Loading
        print("1. Loading data...")
        # Get list of report files
        report_files = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir) if f.endswith('.md')]
        print(f"   Found {len(report_files)} report files.")
        
        # Parse reports
        report_parser = ReportParser(report_files)
        df = report_parser.parse()
        print(f"   Parsed {len(df)} test records.")
        
        # Parse role definitions
        role_parser = RoleDefinitionParser(roles_dir)
        ground_truth = role_parser.parse()
        print(f"   Parsed {len(ground_truth)} role definitions.")
        
        # 2. Analysis
        print("2. Performing analysis...")
        analysis_service = AnalysisService(df, ground_truth)
        
        # Get analysis results
        versatility_results = analysis_service.get_model_versatility()
        inertia_results = analysis_service.get_model_inertia()
        stress_results = analysis_service.get_stress_impact()
        difficulty_results = analysis_service.get_role_difficulty()
        
        print(f"   Analyzed {len(versatility_results)} models.")
        print(f"   Analyzed {len(difficulty_results)} roles.")
        
        # 3. Interpretation
        print("3. Generating interpretations...")
        interpreter = InterpretationEngine()
        
        # Interpret model styles
        model_styles = []
        for model, versatility_score in versatility_results.items():
            inertia_data = inertia_results.get(model, {'top_types': [], 'score': 0.0})
            style_text = interpreter.interpret_model_style(model, versatility_score, inertia_data)
            model_styles.append(style_text)
        
        # Interpret role difficulties
        role_difficulties = []
        for role, avg_score in difficulty_results.items():
            role_mbti = ground_truth.get(role, "Unknown")
            difficulty_text = interpreter.interpret_role_difficulty(role, avg_score, role_mbti, analysis_service.df)
            role_difficulties.append(difficulty_text)
        
        # Interpret stress impact
        stress_text = interpreter.interpret_stress_impact(stress_results)
        
        # 4. Report Generation
        print("4. Generating report...")
        analysis_results = {
            'versatility': versatility_results,
            'inertia': inertia_results,
            'stress': stress_results,
            'difficulty': difficulty_results
        }
        
        interpretation_texts = {
            'model_styles': model_styles,
            'role_difficulties': role_difficulties,
            'stress_impact': stress_text
        }
        
        reporter = ReportGenerator(analysis_results, interpretation_texts)
        reporter.generate(output_file)
        
        print(f"5. Analysis complete!")
        print(f"   Report saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()