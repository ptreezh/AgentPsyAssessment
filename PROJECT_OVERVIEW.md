# AgentPsyAssessment - Project Structure

This document provides an overview of the AgentPsyAssessment project structure.

## Root Directory

```
AgentPsyAssessment/
├── analysis/                  # Analysis Component (Psychometric evaluation and interpretation)
│   ├── __init__.py            # Analysis package initialization
│   ├── analyze_results.py     # Main analysis runner
│   ├── analyze_big5_results.py # Big Five personality analysis
│   ├── analyze_mbti_results.py # MBTI personality analysis
│   ├── analyze_belbin_results.py # Belbin team role analysis
│   └── generate_stress_recommendations.py # Stress testing recommendations
├── llm_assessment/            # Assessment Component (LLM-based questionnaire administration)
│   ├── run_assessment_unified.py # Main assessment runner
│   ├── run_batch_suite.py     # Batch assessment processor
│   ├── services/              # Assessment services (model clients, prompt builders, etc.)
│   └── ...
├── cli.py                     # Main CLI interface
├── setup.py                   # Package setup configuration
├── pyproject.toml             # Modern Python packaging configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── README.md                  # Main project documentation
├── USER_MANUAL.md             # Comprehensive user guide
├── QUICK_START.md            # Quick start guide
├── CONTRIBUTING.md            # Contribution guidelines
├── PROJECT_STRUCTURE.md       # Project structure documentation
├── OPEN_SOURCE_RELEASE_FINAL_SUMMARY.md # Release summary
├── LICENSE                    # MIT License
├── SECURITY.md               # Security policy
├── CODE_OF_CONDUCT.md        # Community guidelines
├── CHANGELOG.md              # Project change log
└── ...
```

## Key Features

### Assessment Component (llm_assessment/)
- Multi-model support (OpenAI, Anthropic, Ollama)
- Configurable personality roles and scenarios
- Temperature and parameter tuning
- Batch processing capabilities
- Context-aware prompting

### Analysis Component (analysis/)
- Big Five personality analysis
- MBTI personality type determination
- Belbin team role analysis
- Stress testing recommendations
- Confidence scoring and validation
- Modular analysis architecture

## Usage Examples

### CLI Commands
```bash
# Assessment commands
python cli.py assess --model gpt-4o --role def
python cli.py batch --model claude-3-5-sonnet --roles a1,a2,b1

# Analysis commands
python cli.py analyze --input results/asses_gpt-4o_def_*.json --analysis-type bigfive
python cli.py analyze --input results/asses_gpt-4o_def_*.json --analysis-type mbti
python cli.py analyze --input results/asses_gpt-4o_def_*.json --analysis-type belbin
python cli.py analyze --input results/combined_assessments.json --analysis-type comprehensive
```

## Contact Information

For questions, support, or collaboration:
- Email: contact@agentpsy.com
- WeChat: 3061176
- Homepage: https://agentpsy.com
- GitHub Issues: https://github.com/ptreezh/AgentPsyAssessment/issues