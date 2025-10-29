# AgentPsyAssessment Project Structure

This document explains the structure of the AgentPsyAssessment project, which consists of two main components:
1. Assessment Component - LLM-based questionnaire administration
2. Analysis Component - Psychometric evaluation and interpretation

## Project Structure Overview

```
AgentPsyAssessment/
├── llm_assessment/              # Assessment Component (LLM-based questionnaire administration)
│   ├── run_assessment_unified.py    # Main assessment runner
│   ├── run_batch_suite.py           # Batch assessment processor
│   ├── services/                    # Assessment services (model clients, prompt builders, etc.)
│   └── ...
├── analysis/                     # Analysis Component (Psychometric evaluation and interpretation)
│   ├── analyze_results.py            # Main analysis runner
│   ├── analyze_big5_results.py       # Big Five personality analysis
│   ├── analyze_mbti_results.py       # MBTI personality analysis
│   ├── analyze_belbin_results.py     # Belbin team role analysis
│   ├── generate_stress_recommendations.py  # Stress testing recommendations
│   └── ...
├── cli.py                        # Main CLI interface
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── README.md                     # Main project documentation
├── USER_MANUAL.md                # Comprehensive user guide
├── QUICK_START.md               # Quick start guide
├── CONTRIBUTING.md               # Contribution guidelines
├── PROJECT_STRUCTURE.md         # Project structure documentation
├── LICENSE                       # MIT License
└── ...
```

## Assessment Component

Located in `llm_assessment/` directory, this component is responsible for:
- Administering psychological questionnaires to LLMs
- Configuring LLM parameters (temperature, roles, context, etc.)
- Collecting and storing raw LLM responses
- Managing different assessment scenarios and conditions

### Key Files:
- `run_assessment_unified.py` - Main entry point for single assessments
- `run_batch_suite.py` - Batch processing for multiple assessments
- `services/` - Supporting services for model interaction and prompt management

## Analysis Component

Located in `analysis/` directory, this component is responsible for:
- Evaluating assessment responses using psychometric models
- Performing Big Five personality analysis
- Conducting MBTI personality analysis
- Performing Belbin team role analysis
- Generating stress testing recommendations
- Creating comprehensive psychological reports

### Key Files:
- `analyze_results.py` - Main analysis entry point
- `analyze_big5_results.py` - Big Five personality analysis
- `analyze_mbti_results.py` - MBTI personality analysis
- `analyze_belbin_results.py` - Belbin team role analysis
- `generate_stress_recommendations.py` - Stress testing recommendations

## Assessment Flow

The complete assessment process follows these steps:

1. **Assessment Component**: Administer questionnaire to LLM
   ```
   python llm_assessment/run_assessment_unified.py --model gpt-4o --role def
   ```

2. **Initial Analysis**: Evaluate initial results
   ```
   python analysis/analyze_results.py --input results/asses_gpt-4o_def_*.json
   ```

3. **Targeted Assessment**: Administer follow-up questions based on initial analysis
   ```
   python llm_assessment/run_assessment_unified.py --model gpt-4o --role targeted --context "focus on neuroticism"
   ```

4. **Comprehensive Analysis**: Generate detailed psychological report
   ```
   python analysis/analyze_results.py --input results/combined_assessments.json --analysis-type comprehensive
   ```

## CLI Interface

The main CLI interface (`cli.py`) provides access to both components:

```
# Assessment commands
python cli.py assess --model gpt-4o --role def
python cli.py batch --model claude-3-5-sonnet --roles a1,a2,b1

# Analysis commands
python cli.py analyze --input results/asses_gpt-4o_def_*.json --analysis-type bigfive
python cli.py analyze --input results/asses_gpt-4o_def_*.json --analysis-type mbti
python cli.py analyze --input results/asses_gpt-4o_def_*.json --analysis-type belbin
python cli.py analyze --input results/combined_assessments.json --analysis-type comprehensive
```

## Development Guidelines

When contributing to the project, consider both components:

1. **Assessment Component**: Focus on improving LLM interaction and response collection
2. **Analysis Component**: Focus on enhancing psychometric evaluation and interpretation
3. **Integration**: Ensure compatibility between components through standardized data formats
4. **Documentation**: Update both component documentation when making changes

## Data Flow

The data flows between components as follows:

1. **Assessment → Analysis**: Raw LLM responses are processed by analysis algorithms
2. **Analysis → Assessment**: Analysis results may inform targeted follow-up assessments
3. **Both Components**: Share common configuration and utility functions

This dual-component structure allows for independent development and improvement of both the LLM-based assessment administration and the psychometric analysis capabilities.